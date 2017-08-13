#!/usr/bin/env python
import os
from app import create_app, db
from app.models import Icinga_info
from flask_script import Manager, Shell

app = create_app(os.getenv('SNOW_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, Icinga_info=Icinga_info)
manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()
