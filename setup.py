#!/usr/bin/env python3
from distutils.core import setup

setup(
    name='zfs-mon',
    version='1.0',
    description='ZFS real-time cache activity monitor',
    author='Andrey Platonov',
    author_email='poluandrey@gmail.com',
    url='https://github.com/tears-of-noobs/zfs-mon.git',
    packages=['zfs_monitor'],
    scripts=['zfs-mon']
)
