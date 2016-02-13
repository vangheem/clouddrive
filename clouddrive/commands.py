from logging import getLogger
import os
import subprocess


TMP_PDF_FILENAME = 'dump.pdf'

logger = getLogger('clouddrive')


class BaseSubProcess(object):
    default_paths = ['/bin', '/usr/bin', '/usr/local/bin']
    bin_name = ''

    if os.name == 'nt':
        close_fds = False
    else:
        close_fds = True

    def __init__(self):
        binary = self._findbinary()
        self.binary = binary
        if binary is None:
            raise IOError("Unable to find %s binary" % self.bin_name)

    def _findbinary(self):
        if 'PATH' in os.environ:
            path = os.environ['PATH']
            path = path.split(os.pathsep)
        else:
            path = self.default_paths

        for directory in path:
            fullname = os.path.join(directory, self.bin_name)
            if os.path.exists(fullname):
                return fullname

        return None

    def _run_command(self, cmd, or_error=False):
        if isinstance(cmd, basestring):
            cmd = cmd.split()
        cmdformatted = ' '.join(cmd)
        logger.info("Running command %s" % cmdformatted)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   close_fds=self.close_fds)
        output, error = process.communicate()
        process.stdout.close()
        process.stderr.close()
        if process.returncode != 0:
            error = u"""Command
%s
finished with return code
%i
and output:
%s
%s""" % (cmdformatted, process.returncode, output, error.decode('utf8'))
            logger.info(error)
            raise Exception(error)
        logger.info("Finished Running Command %s" % cmdformatted)
        if not output:
            if or_error:
                return error
        return output


class MD5SubProcess(BaseSubProcess):
    """
    To get md5 hash of files on the filesystem so
    large files do not need to be loaded into
    memory to be checked
    """
    if os.name == 'nt':
        bin_name = 'md5.exe'
    else:
        bin_name = 'md5'

    def __call__(self, filepath):
        cmd = [self.binary, filepath]
        hashval = self._run_command(cmd)
        return hashval.split('=')[1].strip()

try:
    md5 = MD5SubProcess()
except IOError:
    md5 = None


class MD5SumSubProcess(BaseSubProcess):
    """
    To get md5 hash of files on the filesystem so
    large files do not need to be loaded into
    memory to be checked
    """
    if os.name == 'nt':
        bin_name = 'md5sum.exe'
    else:
        bin_name = 'md5sum'

    def __call__(self, filepath):
        cmd = [self.binary, filepath]
        hashval = self._run_command(cmd)
        return hashval.split('  ')[0].strip()

try:
    if md5 is None:
        md5 = MD5SumSubProcess()
except IOError:
    logger.exception("No md5sum or md5 installed. castle.cms "
                     "will not be able to detect md5 of files.")
    md5 = None
