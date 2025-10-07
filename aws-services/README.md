# Details about AWS Services used
# Region Specification:
The Region is kept as us-east-1 as it is considered as the main region. Moreover, it is the largest AWS region with maximum service availability. Also, the services we plan to use for this project are fully supported by us-east-1 region. Also, we are using third-party API (World Bank and Non-profit Orgnazations for Charity/ Donation). These APIs are often hosted in US and EU regions. Thus, the latency will be low when Lambda call for this APIs. 
# Service 1: S3 bucket 
Amazon S3 is a resilient storage architecture designed to handle vital and primary storage. S3 is an important service for our project as it provides the simplest, cheapest and reliable method to host the web front and store the snapshots or logs from the backend. Furthermore, we do not need to scale our servers manually as S3 comes with a fully managed, multi-AZ services designed for high availability and durability (11 9s). Moreover, it can host a static website by incorporating its website hosting features and this serves our project requirements as the frontend will call API Gateways over HTTPS. Moreover, security is a prime factor in S3. By default, all the new uploads are automatically encrypted with SSE-S3 without incurring any extra costs. Also, lifecycle rules enable us to control expenditure by expiring the obsolete files automatically. Overall, S3 facilitates us to meet our project requirements by incurring low-cost and making the system highly available. 

# Creating Web Hosting Bucket: 
For the Web Bucket, bucket type has been chosen as “General purpose” as it supports multiple availability zone and static web hosting. 

In the Object Ownership section, “ACLs disabled” has been selected because it prevents accidental public exposure through object ACLs. Moreover, all the public access are blocked because it ensures principle of least privilege, which prevents users to misuse the services and mitigates the risk of unintentional data disclosure while uploading the files. This will ensure high security of the S3 bucket.  

For encryption type, SSE-S3 has been selected because it encrypts everything at rest automatically and does not incur extra costs.  

After selecting all the required specification for Web Bucket, we will create the bucket, and the bucket names must be universally unique and should comprise of lowercase letters (a-z), number (0-9), dots (.) and hyphens (-). Apart from these, the length of bucket names should be between 3 to 63 characters long. For our Web Bucket, the bucket name is povertybridge-web-noshin. 

We have enabled bucket versioning as it protects our data further. It stores, fetch and recover every version of every object that are stored in our S3 bucket. Bucket versioning also enables us to recover from unintentional deletes. By default, the system fetches the latest version of data stored.  

# Setting up the Web Bucket: 

We are setting up static website hosting as it is serverless, meaning it scales automatically and has minimum costs. Also, it creates S3 endpoint to host a single point application without involving CloudFront of Route 53. The hosting type has been selected as “Host a Static Website” as it serves the contents directly from the bucket’s root directory and enables us to assign specific index and error files. 

Both the index document and error document are configured to index.html because Single Page Applications use client-side routing instead of server-side routing. For instances, routes such as /countries/US are managed within the browser by JavaScript and not the server. Since these routes have no corresponding files stored in S3 bucket, S3 would usually return 404 error. Configuring the error document as index.html ensures that S3 consistently delivers the application’s root file and enabling the front-end routing logic to display the correct view.  

# Creating Log/ Snapshot Bucket: 

A private S3 bucket for logs or snapshots has been created as it makes the system observable without additional costs and complexities. It gives Lambda an economical place to write structured evidence of events like accumulated JSON responses, “donate” click events, etc. This will help to debug and better understand the issues.  

For the Bucket type, “General purpose” has been selected as it delivers multi-AZ durability and integrates well with CloudTrail and Lambda. 

In the Object Ownership section, “ACLs disabled” has been selected for the same reason as the first bucket, which is to diminish accidental public exposure through object ACLs. Moreover, all the public access are blocked because logs and snapshots are private, and it should not be viewed by public. Hence, blocking all access means that it reduces the chance of accidental exposure of data. 

For the log or snapshot bucket, SSE-S3 is selected for encryption type as it encrypts everything at rest with KMS management and additional costs.  

After configuring the log or snapshot bucket, we will create the bucket successfully. The bucket name of log or snapshot bucket is povertybridge-logs-noshin. 

For lifecycle configuration, new lifecycle rules are created. The current version has been set to expire after 30 days as it will keep the storage clean and affordable. Moreover, incomplete multipart uploads are when clients stop at the middle of uploads. These not only consumes storage but also incur extra costs. Hence, deleting them after 7 days will keep the storage clean and avoid all the hidden extra costs.  

# Service 2: AWS CloudTrail 

CloudTrail captures the changes. It provides a tamper-resistant audit trail across the AWS accounts. Thus, it reinforces the security and the operational efficiency. We have incorporated CloudTrail in our project as it observes and records every change which will help us with root cause analysis, validate least privilege, incident response and integrity check across multi-region. Moreover, CloudTrail is a low-cost set-up, and it logs in the private S3 bucket.  

# Creating CloudTrail: 

A name for CloudTrail is given. Here, it is povertybridge-trail. 
Log file SSE-KMS encryption is selected as off as it uses the default SSE-S3 to prevent KMS setup and additional costs. 

Log file validation is enabled as it does not require extra setup and performs well for integrity checking. For our project, we are keeping CloudWatch as disabled as the Learner Lab does not facilitate turning on CloudWatch logging for trails.  

In the Management events section, Read and Write are selected. This means bucket policies can be read and updated. On the other hand, Data events and Insight events are not selected. Enabling data events would produce lots of events and costs which are essentially not required for our project. Also, insight events are useful for large production projects. Hence, keeping it off means the configuration is kept simple and additional costs are prevented.  

The event history section in CloudTrail displays the recent actions. 

# Service 3: AWS Simple Notification Service 

Simple Notification Service (SNS) is a fast and serverless technique to deliver critical signals to humans or other systems without connecting everything together. Since it is serverless, it will scale automatically without extra costs. Moreover, it is flexible as one publishes can comprises of many subscribers without changing any code on our backend.  
SNS is essential for our project as it will send notification when the API fails, instead of detecting it later. Hence, it will improve the operational efficiency.  

# Configuring SNS: 

To configure SNS, we will go to Amazon SNS in the console and then navigate to Topics. The topic type is selected as Standard because email subscriptions are not supported by FIFO (first-in, first-out) topics. Moreover, Standard topic type offers high throughput. For our SNS, the topic name is set as ops-alarms-topic. 

The subscription standard is selected as email as it serves as the simplest and easiest form of human notification. Also, Email subscription works on any devices, and we can add more subscribers later for ensuring that no one is missing out the alert, and it covers 24/7 availability, without any changes made to the alarms.  

In the endpoint, an email address is given which will send alert to the operator. 
