#!/bin/bash


function error_exit
{
	echo "$1" 1>&2
	exit 0
}

echo "Stopping application"
if sudo service notifications-delivery stop; then
    exit 0
else
    error_exit "Could not stop application"
fi