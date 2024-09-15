import subprocess
from django.core.files.storage import FileSystemStorage


class ArchiveVerifier:
    def __init__(self, filename):
        self.filename = filename
        self.filepath = FileSystemStorage().path(filename)

    def _list_zip(self):
        return subprocess.check_output(['zipinfo', '-1', self.filepath], universal_newlines=True).split()

    def _list_tar(self):
        return subprocess.check_output(['tar', 'tf', self.filepath], universal_newlines=True).split()

    def list_archive(self):
        if self.filename.endswith('.zip'):
            return self._list_zip()
        elif self.filename.endswith(('.tar.gz', '.tar.bz2', '.tar.xz')):
            return self._list_tar()
        else:
            return ('INVALID:', self.filename)

    def is_valid(self):
        content = self.list_archive()
        valid = True
        message = ""
        options = ['unified_diff.patch']
        extensions = ('.qml', '.js', '.png', '.svg', '.qm')
        for o in options:
            if o not in content:
                valid = False
                message += '{} not found in archive!\n'.format(o)
        if len(content) > 3:
            for i in content:
                if i not in options:
                    if not i.endswith(extensions):
                        valid = False
                        message += '\nFile "{}" has a forbidden file extension!'.format(i)
                    if not re.search(r'^[a-zA-Z][a-zA-Z0-9_.+-]*[a-zA-Z0-9]$', i):
                        valid = False
                        message += '\nFile-name "{}" does not match RegEx "^[a-zA-Z][a-zA-Z0-9_.+-]*[a-zA-Z0-9]$"!'.format(i)
        return [valid, message, ' - {}'.format(' - \n'.join(content))]
