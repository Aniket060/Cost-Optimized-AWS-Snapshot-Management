In modern cloud environments, efficient resource management is crucial for cost optimization and operational efficiency. This project focuses on automating the management of EBS snapshots within AWS, aiming to streamline snapshot cleanup and optimize storage costs. The solution leverages AWS Lambda functions triggered by scheduled CloudWatch Events to automatically evaluate and delete unnecessary snapshots based on specific criteria.

With the increasing adoption of cloud infrastructure, organizations seek to reduce operational overhead and lower infrastructure costs. Moving to the cloud offers significant advantages, such as reduced physical infrastructure management and the potential for cost savings. However, cost benefits are realized only when cloud resources are managed effectively.

EBS snapshots are vital for data backup and recovery but can accumulate rapidly, leading to unnecessary storage costs if not managed properly. This project addresses the need for efficient snapshot management by implementing an automated solution that ensures only necessary snapshots are retained while obsolete or unnecessary ones are deleted thus helping to reduce storage costs and optimize cloud resource usage.

Features: 
Automated Snapshot Cleanup: Scheduled Lambda functions periodically check and delete EBS snapshots based on defined criteria which includes Snapshots :
1. Not associated with any existing volume.
2. Associated with a volume not attached to any running EC2 instances.
3. Used for Disaster Recovery
4. Managed by Lifecycle Manager

Setup:
1. Create a Lambda function with following configuration :
   A] Execution set to 10s
   B] Allow permissions for :
                "ec2:DescribeInstances",
                 "ec2:DeleteSnapshot",
                 "ec2:DescribeVolumes",
                 "ec2:DescribeSnapshots"
2. Add an EventBridge Schedule Expression rule of desired time, to the Lambda Function.
3. Deploy the Code
   

