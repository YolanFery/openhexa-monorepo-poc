import typing

from notebook.services.contents.checkpoints import GenericCheckpointsMixin, Checkpoints
from notebook.utils import is_file_hidden
from tornado import web
from notebook.services.contents.manager import ContentsManager
import gcsfs
from traitlets import Unicode
import dateutil.parser
import mimetypes
from base64 import encodebytes, decodebytes


class NoOpCheckpoints(GenericCheckpointsMixin, Checkpoints):
    """requires the following methods:"""

    def create_file_checkpoint(self, content, format, path):
        return {"id": "checkpoint", "last_modified": dateutil.parser.parse("2020-05-29T10:00:00Z")}

    def create_notebook_checkpoint(self, nb, path):
        return {"id": "checkpoint", "last_modified": dateutil.parser.parse("2020-05-29T10:00:00Z")}

    def get_file_checkpoint(self, checkpoint_id, path):
        """ -> {'type': 'file', 'content': <str>, 'format': {'text', 'base64'}}"""

    def get_notebook_checkpoint(self, checkpoint_id, path):
        """ -> {'type': 'notebook', 'content': <output of nbformat.read>}"""

    def delete_checkpoint(self, checkpoint_id, path):
        """deletes a checkpoint for a file"""

    def list_checkpoints(self, path):
        """returns a list of checkpoint models for a given file,
        default just does one per file
        """
        return []

    def rename_checkpoint(self, checkpoint_id, old_path, new_path):
        """renames checkpoint from old path to new path"""


class GCSManager(ContentsManager):
    bucket = Unicode(config=True)
    checkpoints_class = NoOpCheckpoints

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._fs = gcsfs.GCSFileSystem(cache_timeout=0)

    def get(self, path, content: bool = True, type=None, format=None):
        """ Takes a path for an entity and returns its model

        Parameters
        ----------
        path : str
            the API path that describes the relative path for the target
        content : bool
            Whether to include the contents in the reply
        type : str, optional
            The requested type - 'file', 'notebook', or 'directory'.
            Will raise HTTPError 400 if the content doesn't match.
        format : str, optional
            The requested format for file contents. 'text' or 'base64'.
            Ignored if this returns a notebook or directory model.

        Returns
        -------
        model : dict
            the contents model. If content=True, returns the contents
            of the file or directory as well.
        """
        if not self.exists(path):
            raise web.HTTPError(404, "No such file or directory: %s" % path)

        if self.dir_exists(path):
            if type not in (None, "directory"):
                raise web.HTTPError(
                    400, "%s is a directory, not a %s" % (path, type), reason="bad type"
                )
            model = self._dir_model(path, content=content)
        elif type == "notebook" or (type is None and path.endswith(".ipynb")):
            model = self._notebook_model(path, content=content)
        else:
            if type == "directory":
                raise web.HTTPError(
                    400, "%s is not a directory" % path, reason="bad type"
                )
            model = self._file_model(path, content=content, format=format)
        return model

    def file_exists(self, path: str = "") -> bool:
        gcs_path = self._get_gcs_path(path)

        return self._fs.isfile(gcs_path)

    def dir_exists(self, path: str) -> bool:
        gcs_path = self._get_gcs_path(path)

        return self._fs.isdir(gcs_path)

    def _get_gcs_path(self, path: str) -> str:
        bucket_path = self.bucket
        if path == "/":
            return bucket_path

        return f"{bucket_path}/{path.strip('/')}"

    def _base_model(self, path: str):
        gcs_path = self._get_gcs_path(path)
        info = self._fs.info(gcs_path)

        try:
            size = info["size"]
        except KeyError:
            self.log.warning("Unable to get size.")
            size = None

        try:
            last_modified = dateutil.parser.isoparse(info["updated"])
        except (KeyError, ValueError):
            self.log.warning("Invalid mtime %s for %s", info.get("updated"), gcs_path)
            last_modified = dateutil.parser.isoparse("2020-05-29T10:00:00Z")

        try:
            created = dateutil.parser.isoparse(info["timeCreated"])
        except (KeyError, ValueError):  # See above
            self.log.warning(
                "Invalid ctime %s for %s", info.get("timeCreated"), gcs_path
            )
            created = dateutil.parser.isoparse("2020-05-29T10:00:00Z")

        # Create the base model.
        model = {}
        model["name"] = path.rsplit("/", 1)[-1]  # basename?
        model["path"] = path.strip("/")  # gcs_path?
        model["last_modified"] = last_modified
        model["created"] = created
        model["content"] = None
        model["format"] = None
        model["mimetype"] = None
        model["size"] = size
        model["writable"] = True  # TODO: more fine-grained control?

        return model

    def _dir_model(self, path, content=True):
        """Build a model for a directory

        if content is requested, will include a listing of the directory
        """

        model = self._base_model(path)

        gcs_path = self._get_gcs_path(path)

        model["type"] = "directory"
        model["size"] = None
        if content:
            model["content"] = contents = []
            for child in self._fs.listdir(gcs_path):
                child_gcs_path = child["name"]
                child_api_path = child["name"].split("/", 1)[1]
                child_name = child_api_path.split("/")[-1]
                if self.should_list(child_name):
                    if self.allow_hidden or not is_file_hidden(child_gcs_path):
                        contents.append(self.get(child_api_path, content=False))

            model["format"] = "json"

        return model

    def should_list(self, name):
        if name == "":  # empty files returned by GCS / directory markers? (try gsutil ls gs://bucket/dir/)
            return False

        return super().should_list(name)

    def _to_api_path(self, gcs_path: str):
        return gcs_path

    def _file_model(self, path, content=True, format=None):
        """Build a model for a file

        if content is requested, include the file contents.

        format:
          If 'text', the contents will be decoded as UTF-8.
          If 'base64', the raw bytes contents will be encoded as base64.
          If not specified, try to decode as UTF-8, and fall back to base64
        """
        model = self._base_model(path)
        model["type"] = "file"

        gcs_path = self._get_gcs_path(path)
        model["mimetype"] = mimetypes.guess_type(gcs_path)[0]

        if content:
            content, format = self._read_file(gcs_path, format)
            if model["mimetype"] is None:
                default_mime = {
                    "text": "text/plain",
                    "base64": "application/octet-stream",
                }[format]
                model["mimetype"] = default_mime

            model.update(
                content=content, format=format,
            )

        return model

    def _notebook_model(self, path, content=True):
        """Build a notebook model

        if content is requested, the notebook content will be populated
        as a JSON structure (not double-serialized)
        """
        model = self._base_model(path)
        model["type"] = "notebook"
        os_path = self._get_os_path(path)

        if content:
            nb = self._read_notebook(os_path, as_version=4)
            self.mark_trusted_cells(nb, path)
            model["content"] = nb
            model["format"] = "json"
            self.validate_notebook_model(model)

        return model

    def _read_file(self, gcs_path: str, format: str):
        """Read a non-notebook file.

        os_path: The path to be read.
        format:
          If 'text', the contents will be decoded as UTF-8.
          If 'base64', the raw bytes contents will be encoded as base64.
          If not specified, try to decode as UTF-8, and fall back to base64
        """
        if not self._fs.isfile(gcs_path):
            raise web.HTTPError(400, "Cannot read non-file %s" % gcs_path)

        with self._fs.open(gcs_path, "rb") as f:
            bcontent = f.read()

        if format is None or format == "text":
            # Try to interpret as unicode if format is unknown or if unicode
            # was explicitly requested.
            try:
                return bcontent.decode("utf8"), "text"
            except UnicodeError:
                if format == "text":
                    raise web.HTTPError(
                        400, "%s is not UTF-8 encoded" % gcs_path, reason="bad format",
                    )
        return encodebytes(bcontent).decode("ascii"), "base64"
