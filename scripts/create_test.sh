#!/usr/bin/env bash
echo -e $TEST_FILE_CONTENTS > $TEST_FOLDER_LOCAL$TEST_FILE
aws s3 rm $SOURCE_S3_BUCKET/$TEST_FILE --profile $AWS_PROFILE
aws s3 rm $DESTINATION_S3_BUCKET/$TEST_FILE_REPLACED --profile $AWS_PROFILE
aws s3 cp $TEST_FOLDER_LOCAL$TEST_FILE $SOURCE_S3_BUCKET --profile $AWS_PROFILE
