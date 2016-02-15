#!/usr/bin/env python

from __future__ import print_function

import os

from flask.ext.script import Manager, Server

from notifications_delivery.app import create_app
from notifications_delivery.processor.sqs_processor import process_all_queues

application = create_app()
manager = Manager(application)
port = int(os.environ.get('PORT', 6013))
manager.add_command("runserver", Server(host='0.0.0.0', port=port))


@manager.command
def list_routes():
    """List URLs of all application routes."""
    for rule in sorted(application.url_map.iter_rules(), key=lambda r: r.rule):
        print("{:10} {}".format(", ".join(rule.methods - set(['OPTIONS', 'HEAD'])), rule.rule))


@manager.command
def process_queues():
    """Process all queues pulling one message from the queue."""
    # TODO possibly in the future have the prefix option on the management command.
    queue_name_prefix = application.config['NOTIFICATION_QUEUE_PREFIX']
    process_all_queues(application.config, queue_name_prefix)


if __name__ == '__main__':
    manager.run()
