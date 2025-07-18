# Deploy to Oracle Cloud Free Tier

## What You Get (Forever Free):
- Up to 4 VMs (2 AMD + 2 ARM)
- 24GB RAM total (ARM instances)
- 200GB storage
- 10TB bandwidth/month
- No sleep time, no restrictions

## Steps:

1. **Sign up for Oracle Cloud**
   - Go to cloud.oracle.com
   - Need credit card (won't be charged)
   - Choose home region carefully (can't change later)

2. **Create a VM Instance**
   - Go to Compute > Instances
   - Create Instance
   - Choose "Always Free Eligible" shape
   - Select Ubuntu 22.04
   - Add your SSH key

3. **Setup Your Server**
   ```bash
   # SSH into your instance
   ssh ubuntu@your-instance-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and requirements
   sudo apt install python3-pip python3-venv nginx -y
   
   # Clone your app
   git clone https://github.com/Harry166/stro.git
   cd stro
   
   # Setup virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Install and configure gunicorn
   pip install gunicorn
   ```

4. **Setup Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain-or-ip;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Run with systemd**
   Create service file for auto-start on boot

## Pros:
- Completely free forever
- No limitations on usage
- Professional-grade infrastructure
- Can run multiple apps

## Cons:
- Requires Linux knowledge
- Manual setup needed
- Need to manage security yourself
