#!/usr/bin/env python

from __future__ import print_function

import os

from flask.ext.script import Manager, Server

from notifications_delivery.app import create_app
from notifications_delivery.processor.sqs_processor import process_all_queues

application = create_app(os.getenv('NOTIFY_DELIVERY_ENVIRONMENT') or 'development')
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
    process_all_queues(application.config)


if __name__ == '__main__':
    manager.run()
