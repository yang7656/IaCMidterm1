#!/usr/bin/env python
from constructs import Construct
from cdktf import (
    App,
    TerraformStack,
    TerraformOutput,
    RemoteBackend,
    NamedRemoteWorkspace,
)
from imports.aws import (
    provider,
    s3_bucket,
    s3_bucket_website_configuration,
    s3_bucket_object,
    s3_bucket_policy,
    s3_bucket_public_access_block,
    s3_bucket_ownership_controls,
    s3_bucket_acl
)

from imports.aws.s3_bucket_website_configuration import S3BucketWebsiteConfigurationIndexDocument
from imports.aws.s3_bucket_ownership_controls import S3BucketOwnershipControlsRule

import mimetypes
import os
import json

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # define resources here
        provider.AwsProvider(self, "AWS", region="us-west-1")
        
        bucket = s3_bucket.S3Bucket(self, "midtermBucket", bucket="midterm-s3")
                    
        s3_bucket_website_configuration.S3BucketWebsiteConfiguration(
            self,
            id_="midterm_id",
            bucket=bucket.id,
            index_document=S3BucketWebsiteConfigurationIndexDocument(suffix="index.html")
        )
        
        public_access = s3_bucket_public_access_block.S3BucketPublicAccessBlock(
            self, 
            "midterm_public",
            bucket=bucket.id
        )
                        
        ownership = s3_bucket_ownership_controls.S3BucketOwnershipControls(
            self, 
            "midterm_ownership",
            bucket=bucket.id,
            rule=S3BucketOwnershipControlsRule(object_ownership="BucketOwnerEnforced")
        )
      
        bucket_policy = s3_bucket_policy.S3BucketPolicy(
            self, 
            "midterm_policy",
            bucket=bucket.id,
            depends_on=[ ownership, public_access ],
            policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": f"arn:aws:s3:::midterm-s3/*"
                }]
            })
        )
                        
        file_path = os.path.abspath("index.html")
        midterm_type, _ = mimetypes.guess_type(file_path)
                   
        s3_bucket_object.S3BucketObject(
            self, 
            "website_index",
            bucket=bucket.id,
            depends_on=[bucket_policy],
            key="index.html",
            source=file_path,
            content_type=midterm_type
        )

app = App()
MyStack(app, "midtermS3")

app.synth()