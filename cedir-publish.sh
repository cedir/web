#!/bin/bash
# Script for publishing content
# Author: Walter M Brunetti
# Version: 1.0

echo "Running update..."
svn update

echo "Restarting Apache..."
/etc/init.d/apache2 restart

echo "Done. Cedir is updated."

exit