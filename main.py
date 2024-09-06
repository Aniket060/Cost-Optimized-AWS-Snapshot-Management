import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # Define counters
    total_snapshots = 0
    deleted_snapshots = 0
    ignored_snapshots = {
        'managed_by_dlm': 0,
        'disaster_recovery': 0,
        'volume_not_attached': 0,
        'volume_not_found': 0,
        'volume_attached_to_running_instance': 0
    }
    
    # Get all EBS snapshots
    response = ec2.describe_snapshots(OwnerIds=['self'])
    snapshots = response['Snapshots']
    total_snapshots = len(snapshots)
    
    # Get all active EC2 instance IDs
    instances_response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    active_instance_ids = set()
    
    for reservation in instances_response['Reservations']:
        for instance in reservation['Instances']:
            active_instance_ids.add(instance['InstanceId'])
    
    # Iterate through each snapshot and apply the deletion criteria
    for snapshot in snapshots:
        snapshot_id = snapshot['SnapshotId']
        volume_id = snapshot.get('VolumeId')
        tags = {tag['Key']: tag['Value'] for tag in snapshot.get('Tags', [])}
        creation_time = snapshot['StartTime']
        
        # Check if the snapshot is tagged for disaster recovery
        if tags.get('BackupType') == 'DisasterRecovery':
            ignored_snapshots['disaster_recovery'] += 1
            continue
        
        # Check if the snapshot is managed by DLM
        if tags.get('BackupType') == 'DLM':
            ignored_snapshots['managed_by_dlm'] += 1
            continue
        
        # Check if the snapshot is associated with a volume
        if volume_id:
            try:
                volume_response = ec2.describe_volumes(VolumeIds=[volume_id])
                if not volume_response['Volumes'][0]['Attachments']:
                    # Volume is not attached to any instance
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    deleted_snapshots += 1
                    ignored_snapshots['volume_not_attached'] += 1
                    print(f"Deleted snapshot {snapshot_id} as its volume is not attached to any instance.")
                    continue
            except ec2.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                    # Volume associated with the snapshot is not found
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    deleted_snapshots += 1
                    ignored_snapshots['volume_not_found'] += 1
                    print(f"Deleted snapshot {snapshot_id} as its associated volume was not found.")
                    continue
        
        # Check if the volume is attached to any running instance
        if volume_id:
            volume_response = ec2.describe_volumes(VolumeIds=[volume_id])
            volume_attachments = volume_response['Volumes'][0]['Attachments']
            if any(att['InstanceId'] in active_instance_ids for att in volume_attachments):
                ignored_snapshots['volume_attached_to_running_instance'] += 1
                continue
        
        # If none of the conditions are met, delete the snapshot
        ec2.delete_snapshot(SnapshotId=snapshot_id)
        deleted_snapshots += 1
        print(f"Deleted snapshot {snapshot_id} based on deletion criteria.")
    
    # Prepare the response
    response = {
        "statusCode": 200,
        "body": {
            "TotalSnapshots": total_snapshots,
            "DeletedSnapshots": deleted_snapshots,
            "IgnoredSnapshots": ignored_snapshots
        }
    }
    
    return response
