#!/bin/bash

## Steps:
# 1- Install mega-cmd
# 2- Create file with mega configurations in home/.megacmd.json:
# nano $HOME/.megacmd.json
# {
# "User" : "account@mail.com",
# "Password" : "password",
# "DownloadWorkers": 4,
# "UploadWorkers": 4,
# "SkipSameSize" : true,
# "Verbose": 1
# }
# 3- Create directory of backups and give permissions to write (chmod a+w backup_file)
# 4- Install mailutils (sudo apt install mailutils)
# 5- Set up ssmtp https://wiki.archlinux.org/index.php/SSMTP
# 4- Set up cron:
# Format of cron:
# MINUTE HOUR DAY MONTH DAY_OF_THE_WEEK
# Example:
#
# crontab -e
# 30 8 * * * /home/apps/scripts/automatic_backup.sh
#
# (Every day at 8:30)

FILENAME_OUTPUT=db.out
DIRECTORY_BACKUP=/home/dani/Trabajo
DIRECTORY_MEGA=backups/
OUTPUT="$(date)\n"
DIRECTORY_LOG=/home/dani/.logs/automatic_backups.log
OK_MESSAGE='Upload finished'
MAIL_SUBJECT="Error with backups"
MAIL_ERROR_MESSAGE="There was an error while creating the db backup. Please see the logs in the server. Direction of the logs: $DIRECTORY_LOG"
MAIL_DESTINATARY="account@gmail.com"
MAIL_SENDER="account@gmail.com"

sendmail() {
	mail -s $MAIL_SUBJECT $MAIL_DESTINATARY <<< $MAIL_ERROR_MESSAGE
}

make_backup() {
	OUTPUT="$OUTPUT - Dumping database to backup directory...\n"
	pg_dump cedir_db > $DIRECTORY_BACKUP/$FILENAME_OUTPUT
	
	if [ -s $DIRECTORY_BACKUP/$FILENAME_OUTPUT ]
	then
		OUTPUT="$OUTPUT Dump database success\n"
		SUCCESS_BACKUP=0
	else
		OUTPUT="$OUTPUT There was an error during pgdump. File generated is empty\n"
		sendmail
		SUCCESS_BACKUP=1
	fi
}

upload_backup() {
	OUTPUT="$OUTPUT - Uploading backup...\n"
	megacmd_put_output=$(mega-put $DIRECTORY_BACKUP/$FILENAME_OUTPUT ./$DIRECTORY_MEGA)
	if [[ $megacmd_put_output == *$OK_MESSAGE ]]
	then
		OUTPUT="$OUTPUT - Uploading success.\n Process complete\n"
	else
		OUTPUT="$OUTPUT - There was an error while uploading file to mega\n"
		sendmail
	fi
}

OUTPUT="$OUTPUT - Starting process -\n"
make_backup

if [ $SUCCESS_BACKUP -eq 0 ]
then
	upload_backup
fi

printf "$OUTPUT\n" >> $DIRECTORY_LOG