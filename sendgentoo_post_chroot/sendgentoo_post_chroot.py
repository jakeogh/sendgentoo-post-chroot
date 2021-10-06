#!/usr/bin/env python3
# -*- coding: utf8 -*-

# flake8: noqa           # flake8 has no per file settings :(
# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=C0114  #      Missing module docstring (missing-module-docstring)
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement
# pylint: disable=C0305  # Trailing newlines editor should fix automatically, pointless warning
# pylint: disable=C0413  # TEMP isort issue [wrong-import-position] Import "from pathlib import Path" should be placed at the top of the module [C0413]

import logging

logging.basicConfig(level=logging.INFO)
import os
import sys
#import time
from signal import SIG_DFL
from signal import SIGPIPE
from signal import signal

if len(sys.argv) <= 2:
    print(sys.argv[0], "arguments required")
    sys.exit(1)


def syscmd(cmd):
    print(cmd, file=sys.stderr)
    os.system(cmd)

syscmd('emerge --quiet dev-vcs/git -1 -u')
syscmd('emerge --sync')
syscmd('emerge --quiet sys-apps/portage -1 -u')
syscmd('emerge --quiet dev-python/click -1 -u')
syscmd('emerge --quiet app-eselect/eselect-repository -1 -u')
syscmd('emerge --quiet dev-python/sh -1 -u')
import sh

os.makedirs('/etc/portage/repos.conf', exist_ok=True)
if 'jakeogh' not in sh.eselect('repository', 'list', '-i'):
    sh.eselect('repository', 'add', 'jakeogh', 'git', 'https://github.com/jakeogh/jakeogh', _out=sys.stdout, _err=sys.stderr)   # ignores http_proxy
sh.emaint('sync', '-r', 'jakeogh', _out=sys.stdout, _err=sys.stderr)  # this needs git
if 'pentoo' not in sh.eselect('repository', 'list', '-i'):  # for fchroot (next time)
    sh.eselect('repository', 'enable', 'pentoo', _out=sys.stdout, _err=sys.stderr)   # ignores http_proxy
sh.emaint('sync', '-r', 'pentoo', _out=sys.stdout, _err=sys.stderr)  # this needs git

_env = os.environ.copy()
_env['CONFIG_PROTECT'] = '-*'


def emerge_force(package):
    emerge_command = sh.emerge.bake('--with-bdeps=y', '--quiet', '--tree', '--usepkg=n', '--ask', 'n', '--autounmask', '--autounmask-write', package, _env=_env, _out=sys.stdout, _err=sys.stderr, _in=sys.stdin, _ok_code=[0,1])

    #emerge_command(_env=_env, _out=sys.stdout, _err=sys.stderr, _in=sys.stdin, _ok_code=[0,1])
    emerge_command('-pv', _env=_env, _out=sys.stdout, _err=sys.stderr, _in=sys.stdin, _ok_code=[0,1])
    emerge_command('--autounmask-continue', _env=_env, _out=sys.stdout, _err=sys.stderr, _in=sys.stdin)


emerge_force('pathtool')
emerge_force('portagetool')
emerge_force('devicetool')
emerge_force('boottool')
emerge_force('sendgentoo-post-chroot')

#sh.emerge('--with-bdeps=y', '--quiet', '--tree', '--usepkg=n', '--ask', 'n', '--autounmask', '--autounmask-write', 'sendgentoo-post-chroot', _env=_env, _out=sys.stdout, _err=sys.stderr, _in=sys.stdin, _ok_code=[0,1])
#sh.emerge('--with-bdeps=y', '--quiet', '--tree', '--usepkg=n', '--ask', 'n', '--autounmask', '--autounmask-write', 'sendgentoo-post-chroot', _env=_env, _out=sys.stdout, _err=sys.stderr, _in=sys.stdin)
#
#sh.emerge('--with-bdeps=y', '--quiet', '--tree', '--usepkg=n', '--ask', 'n', '--autounmask', '--autounmask-write', 'portagetool', _env=_env, _out=sys.stdout, _err=sys.stderr, _in=sys.stdin, _ok_code=[0,1])
#sh.emerge('--with-bdeps=y', '--quiet', '--tree', '--usepkg=n', '--ask', 'n', '--autounmask', '--autounmask-write', 'portagetool', _env=_env, _out=sys.stdout, _err=sys.stderr, _in=sys.stdin)
#
#sh.emerge('--with-bdeps=y', '--quiet', '--tree', '--usepkg=n', '--ask', 'n', '--autounmask', '--autounmask-write', 'boottool', _env=_env, _out=sys.stdout, _err=sys.stderr, _in=sys.stdin, _ok_code=[0,1])
#sh.emerge('--with-bdeps=y', '--quiet', '--tree', '--usepkg=n', '--ask', 'n', '--autounmask', '--autounmask-write', 'boottool', _env=_env, _out=sys.stdout, _err=sys.stderr, _in=sys.stdin)
import click

signal(SIGPIPE, SIG_DFL)
from pathlib import Path
from typing import ByteString
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from asserttool import eprint
from asserttool import ic
from asserttool import nevd
from boottool import install_grub
from mounttool import path_is_mounted
from pathtool import gurantee_symlink
from pathtool import write_line_to_file
from portagetool import add_accept_keyword
from portagetool import install_package
from portagetool import install_package_force


@click.command()
@click.option('--stdlib', is_flag=False, required=False, type=click.Choice(['glibc', 'musl', 'uclibc']))
@click.option('--boot-device', is_flag=False, required=True)
@click.option('--march', is_flag=False, required=True, type=click.Choice(['native', 'nocona']))
@click.option('--root-filesystem', is_flag=False, required=True,  type=click.Choice(['ext4', 'zfs', '9p']), default="ext4")
@click.option('--newpasswd', is_flag=False, required=True)
@click.option('--pinebook-overlay', is_flag=True,  required=False)
@click.option('--kernel', is_flag=False, required=True, type=click.Choice(['gentoo-sources', 'pinebookpro-manjaro-sources']),default='gentoo-sources')
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_context
def cli(ctx,
        stdlib: str,
        boot_device: Path,
        march: str,
        root_filesystem: str,
        newpasswd: str,
        pinebook_overlay: bool,
        kernel: str,
        verbose: bool,
        debug: bool,
        ):

    null, end, verbose, debug = nevd(ctx=ctx,
                                     printn=False,
                                     ipython=False,
                                     verbose=verbose,
                                     debug=debug,)


    #musl: http://distfiles.gentoo.org/experimental/amd64/musl/HOWTO
    #spark: https://github.com/holman/spark.git
    #export https_proxy="http://192.168.222.100:8888"
    #export http_proxy="http://192.168.222.100:8888"
    #source /home/cfg/_myapps/sendgentoo/sendgentoo/utils.sh
    if verbose:
        ic(stdlib, boot_device, march, root_filesystem, newpasswd, pinebook_overlay, kernel)

    assert path_is_mounted(Path("/boot/efi"), verbose=verbose, debug=debug)

    #sh.emerge('--sync', _out=sys.stdout, _err=sys.stderr)

    os.makedirs(Path('/var/db/repos/gentoo'), exist_ok=True)

    if stdlib == 'musl':
        if 'musl' not in sh.eselect('repository', 'list', '-i'):  # for fchroot (next time)
            sh.eselect('repository', 'enable', 'musl', _out=sys.stdout, _err=sys.stderr)   # ignores http_proxy
        sh.emaint('sync', '-r', 'musl', _out=sys.stdout, _err=sys.stderr)  # this needs git
        sh.emerge('-uvNDq', '@world', _out=sys.stdout, _err=sys.stderr)

    zfs_module_mode = "module"
    #env-update || exit 1
    #source /etc/profile || exit 1

    #here down is stuff that might not need to run every time
    # ---- begin run once, critical stuff ----

    sh.passwd('-d', 'root')
    sh.chmod('+x', '-R', '/home/cfg/sysskel/etc/local.d/')
    #sh.eselect('python', 'list')  # depreciated
    sh.eselect('profile', 'list', _out=sys.stdout, _err=sys.stderr)
    write_line_to_file(path=Path('/etc') / Path('locale.gen'),
                       line='en_US.UTF-8 UTF-8\n',
                       unique=True,
                       verbose=verbose,
                       debug=debug,)
    sh.locale_gen(_out=sys.stdout, _err=sys.stderr)  # hm, musl does not need this? dont fail here for uclibc or musl

    write_line_to_file(path=Path('/etc') / Path('env.d') / Path('02collate'),
                       line='LC_COLLATE="C"\n',
                       unique=True,
                       verbose=verbose,
                       debug=debug,)

    # not /etc/localtime, the next command does that
    write_line_to_file(path=Path('/etc') / Path('timezone'),
                       line='US/Arizona\n',
                       unique=True,
                       verbose=verbose,
                       debug=debug,)

    sh.emerge('--config', 'timezone-data')
    sh.grep('processor', '/proc/cpuinfo')

    cores = len(sh.grep('processor', '/proc/cpuinfo').splitlines())
    write_line_to_file(path=Path('/etc') / Path('portage') / Path('makeopts.conf'),
                       line='MAKEOPTS="-j{cores}"\n'.format(cores=cores),
                       unique=True,
                       verbose=verbose,
                       debug=debug,)

    write_line_to_file(path=Path('/etc') / Path('portage') / Path('cflags.conf'),
                       line='CFLAGS="-march={march} -O2 -pipe -ggdb"\n'.format(march=march),
                       unique=True,
                       verbose=verbose,
                       debug=debug,)

    # right here, portage needs to get configured... this stuff ends up at the end of the final make.conf
    write_line_to_file(path=Path('/etc') / Path('portage') / Path('make.conf'),
                       line='ACCEPT_KEYWORDS="~amd64"\n',
                       unique=True,
                       verbose=verbose,
                       debug=debug,)

    write_line_to_file(path=Path('/etc') / Path('portage') / Path('make.conf'),
                       line='EMERGE_DEFAULT_OPTS="--quiet-build=y --tree --nospinner"\n',
                       unique=True,
                       verbose=verbose,
                       debug=debug,)

    write_line_to_file(path=Path('/etc') / Path('portage') / Path('make.conf'),
                       line='FEATURES="parallel-fetch splitdebug buildpkg"\n',
                       unique=True,
                       verbose=verbose,
                       debug=debug,)

    #source /etc/profile

    # otherwise gcc compiles twice
    write_line_to_file(path=Path('/etc') / Path('portage') / Path('package.use') / Path('gcc'),
                       line='sys-devel/gcc fortran\n',
                       unique=True,
                       verbose=verbose,
                       debug=debug,)

    # works, but quite a delay for an installer
    #install_package('gcc', verbose=verbose)
    #sh.gcc_config('latest', _out=sys.stdout, _err=sys.stderr)

    # install kernel and update symlink (via use flag)
    os.environ['KCONFIG_OVERWRITECONFIG'] = '1' # https://www.mail-archive.com/lede-dev@lists.infradead.org/msg07290.html

    # required so /usr/src/linux exists
    write_line_to_file(path=Path('/etc') / Path('portage') / Path('package.use') / Path(kernel),
                       line='sys-kernel/{kernel} symlink\n'.format(kernel=kernel),
                       unique=True,
                       verbose=verbose,
                       debug=debug,)

    install_package('sys-kernel/{kernel}'.format(kernel=kernel))
    install_package('grub')
    install_package('dev-util/strace')
    install_package('memtest86+') # do before generating grub.conf

    os.makedirs('/usr/src/linux_configs', exist_ok=True)

    try:
        os.unlink('/usr/src/linux/.config')           # shouldnt exist yet
    except FileNotFoundError:
        pass

    try:
        os.unlink('/usr/src/linux_configs/.config')           # shouldnt exist yet
    except FileNotFoundError:
        pass

    if not Path('/usr/src/linux/.config').is_symlink():
        #sh.ln('-s', '/home/cfg/sysskel/usr/src/linux_configs/.config', '/usr/src/linux_configs/.config')
        #sh.ln('-s', '/usr/src/linux_configs/.config', '/usr/src/linux/.config')
        gurantee_symlink(relative=False, target='/home/cfg/sysskel/usr/src/linux_configs/.config', link_name='/usr/src/linux_configs/.config', verbose=verbose, debug=debug,)
        gurantee_symlink(relative=False, target='/usr/src/linux_configs/.config', link_name='/usr/src/linux/.config', verbose=verbose, debug=debug,)

    try:
        sh.grep("CONFIG_TRIM_UNUSED_KSYMS is not set", '/usr/src/linux/.config')
    except sh.ErrorReturnCode_1 as e:
        ic(e)
        eprint("ERROR: Rebuild the kernel with CONFIG_TRIM_UNUSED_KSYMS must be =n")
        sys.exit(1)

    try:
        sh.grep("CONFIG_FB_EFI is not set", '/usr/src/linux/.config', _ok_code=[1])
    except sh.ErrorReturnCode_1 as e:
        ic(e)
        eprint("ERROR: Rebuild the kernel with CONFIG_FB_EFI=y")
        sys.exit(1)

    #add_accept_keyword("sys-fs/zfs-9999")
    #add_accept_keyword("sys-fs/zfs-kmod-9999")

    write_line_to_file(path=Path('/etc') / Path('fstab'),
                       line='#<fs>\t<mountpoint>\t<type>\t<opts>\t<dump/pass>\n',
                       unique=False,
                       unlink_first=True,
                       verbose=verbose,
                       debug=debug,)

    #ln -sf /proc/self/mounts /etc/mtab
    #grub-install --compress=no --target=x86_64-efi --efi-directory=/boot/efi --boot-directory=/boot --removable --recheck --no-rs-codes "${boot_device}" || exit 1
    #grub-install --compress=no --target=i386-pc --boot-directory=/boot --recheck --no-rs-codes "${boot_device}" || exit 1

    gurantee_symlink(relative=False, target='/home/cfg/sysskel/etc/skel/bin', link_name='/root/bin', verbose=verbose, debug=debug,)
    #sh.ln('-s', '/home/cfg/sysskel/etc/skel/bin', '/root/bin')

    install_package('gradm')  # required for gentoo-hardened RBAC

    # required for genkernel
    write_line_to_file(path=Path('/etc') / Path('portage') / Path('package.use') / Path('util-linux'),
                       line='sys-apps/util-linux static-libs\n',
                       unique=False,
                       unlink_first=True,
                       verbose=verbose,
                       debug=debug,)

    write_line_to_file(path=Path('/etc') / Path('portage') / Path('package.license'),
                       line='sys-kernel/linux-firmware linux-fw-redistributable no-source-code\n',
                       unique=True,
                       unlink_first=False,
                       verbose=verbose,
                       debug=debug,)

    install_package('genkernel')
    #install_package('app-eselect/eselect-repository')
    os.makedirs('/etc/portage/repos.conf', exist_ok=True)

    with open('/etc/portage/proxy.conf', 'r') as fh:
        for line in fh:
            line = line.strip()
            line = ''.join(line.split('"'))
            line = ''.join(line.split('#'))
            if line:
                ic(line)
                key = line.split('=')[0]
                value = line.split('=')[1]
                os.environ[key] = value
                write_line_to_file(path=Path('/etc') / Path('wgetrc'),
                                   line='{}\n'.format(line),
                                   unique=True,
                                   unlink_first=False,
                                   verbose=verbose,
                                   debug=debug,)

    write_line_to_file(path=Path('/etc') / Path('wgetrc'),
                       line='use_proxy = on\n',
                       unique=True,
                       unlink_first=False,
                       verbose=verbose,
                       debug=debug,)

    #if 'jakeogh' not in sh.eselect('repository', 'list', '-i'):
    #    sh.eselect('repository', 'add', 'jakeogh', 'git', 'https://github.com/jakeogh/jakeogh')   # ignores http_proxy
    ##git config --global http.proxy http://192.168.222.100:8888
    #install_package('dev-vcs/git')
    #sh.emaint('sync', '-r', 'jakeogh')  # this needs git

    if pinebook_overlay:
        if 'pinebookpro-overlay' not in sh.eselect('repository', 'list', '-i'):
            sh.eselect('repository', 'add', 'pinebookpro-overlay', 'git', 'https://github.com/Jannik2099/pinebookpro-overlay.git')   # ignores http_proxy
        sh.emerge('--sync', 'pinebookpro-overlay')
        sh.emerge('-u', 'pinebookpro-profile-overrides')

    install_package_force('compile-kernel')  # requires jakeogh overlay
    sh.compile_kernel('--no-check-boot', _out=sys.stdout, _err=sys.stderr, _ok_code=[0, 1])
    #sh.cat /home/cfg/sysskel/etc/fstab.custom >> /etc/fstab

    # this cant be done until memtest86+ and the kernel are ready
    ctx.invoke(install_grub,
               boot_device=boot_device,
               verbose=verbose,
               debug=debug,)
    #install_grub_command = sh.Command('/home/cfg/_myapps/sendgentoo/sendgentoo/post_chroot_install_grub.sh', boot_device)
    #install_grub_command(_out=sys.stdout, _err=sys.stderr)

    sh.rc_update('add', 'zfs-mount', 'boot', _out=sys.stdout, _err=sys.stderr, _ok_code=[0, 1]) # dont exit if this fails
    install_package('dhcpcd')  # not in stage3

    #sh.ln('-rs', '/etc/init.d/net.lo', '/etc/init.d/net.eth0', _out=sys.stdout, _err=sys.stderr)
    os.symlink('/etc/init.d/net.lo', '/etc/init.d/net.eth0')
    sh.rc_update('add', 'net.eth0', 'default', _out=sys.stdout, _err=sys.stderr)

    install_package('netdate')
    sh.date(_out=sys.stdout, _err=sys.stderr)
    sh.netdate('time.nist.gov', _out=sys.stdout, _err=sys.stderr)
    sh.date(_out=sys.stdout, _err=sys.stderr)

    install_package('gpm')
    sh.rc_update('add', 'gpm', 'default', _out=sys.stdout, _err=sys.stderr)   #console mouse support

    #install_package('elogind')
    #rc-update add elogind default

    install_package('app-admin/sysklogd')
    sh.rc_update('add', 'sysklogd', 'default', _out=sys.stdout, _err=sys.stderr)  # syslog-ng hangs on boot... bloated

    os.makedirs('/etc/portage/package.mask', exist_ok=True)
    install_package('unison')
    #sh.eselect('unison', 'list') #todo

    sh.perl_cleaner('--reallyall', _out=sys.stdout, _err=sys.stderr)
    install_package('app-portage/repoman')
    install_package('app-editors/vim')
    install_package('www-client/links')
    #install_package('dev-db/redis')  # later on, fix_cfg_perms will try to use the redis:redis user
    install_package('app-admin/sudo')
    install_package('app-text/tree')
    install_package('sys-fs/safecopy')
    install_package('sys-process/lsof')
    install_package('sys-apps/lshw')
    install_package('app-editors/hexedit')
    install_package('sys-process/glances')
    install_package('app-admin/pydf')
    install_package('sys-fs/ncdu')
    install_package('app-portage/gentoolkit') #equery
    install_package('sys-process/htop')
    install_package('sys-fs/ddrescue')
    #install_package('sys-process/cronie')  # done in postreboot set
    install_package('net-dns/bind-tools')
    install_package('app-admin/sysstat')   #mpstat
    install_package('wpa_supplicant')
    install_package('sys-apps/sg3_utils')
    install_package('dev-util/fatrace')
    install_package('sys-apps/smartmontools')
    sh.rc_update('add', 'smartd', 'default')
    install_package('sys-fs/multipath-tools')
    install_package('sys-apps/usbutils')  # lsusb for /etc/local.d/ scripts

    install_package('net-fs/nfs-utils')
    sh.rc_update('add', 'nfs', 'default')
    install_package('dev-python/distro')  # distro detection in boot scripts

    install_package('net-libs/libnfsidmap')  # rpc.idmapd

    install_package('sys-power/powertop')
    install_package('sys-power/upower')
    install_package('sys-apps/dmidecode')
    install_package('app-misc/tmux')
    sh.rc_update('add', 'dbus', 'default')

    install_package('dev-util/ccache')
    os.makedirs('/var/cache/ccache', exist_ok=True)
    sh.chown('root:portage', '/var/cache/ccache')
    sh.chmod('2775', '/var/cache/ccache')

    install_package('dev-util/ctags')  # so vim/nvim dont complain

    #sh.ls('/etc/ssh/sshd_config', '-al', _out=sys.stdout, _err=sys.stderr)

    write_line_to_file(path=Path('/etc') / Path('ssh') / Path('sshd_config'),
                       line='PermitRootLogin yes\n',
                       unique=True,
                       unlink_first=False,
                       verbose=verbose,
                       debug=debug,)

    install_package_force('replace-text')

    os.environ['LANG'] = "en_US.UTF8"  # to make click happy

    write_line_to_file(path=Path('/etc') / Path('inittab'),
                       line='PermitRootLogin yes\n',
                       unique=True,
                       unlink_first=False,
                       verbose=verbose,
                       debug=debug,)

    #replace_text_in_file(path='/etc/inittab',
    #                     match="c1:12345:respawn:/sbin/agetty 38400 tty1 linux",
    #                     replacement="c1:12345:respawn:/sbin/agetty 38400 tty1 linux --noclear",

    #grep noclear /etc/inittab || \
    with open('/etc/iniitab', 'r') as fh:
        if not 'noclear' in fh.read():
            sh.replace_text('--match', "c1:12345:respawn:/sbin/agetty 38400 tty1 linux", '--replacement', "c1:12345:respawn:/sbin/agetty 38400 tty1 linux --noclear", '/etc/inittab')

    install_package('sys-apps/moreutils') # need sponge for the next command
    #grep "c7:2345:respawn:/sbin/agetty 38400 tty7 linux" /etc/inittab || { cat /etc/inittab | /home/cfg/text/insert_line_after_match "c6:2345:respawn:/sbin/agetty 38400 tty6 linux" "c7:2345:respawn:/sbin/agetty 38400 tty7 linux" | sponge /etc/inittab ; }
    #echo "$(date) $0 complete" | tee -a /install_status

if __name__ == '__main__':
    # pylint: disable=E1120
    cli()
