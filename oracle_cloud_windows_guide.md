# Oracle Cloud Free Tier Setup Guide for Windows Users

## Prerequisites on Windows

1. **Create SSH Keys** (if you don't have them):
   ```powershell
   # Open PowerShell and run:
   ssh-keygen -t rsa -b 2048
   # Press Enter for default location (~/.ssh/id_rsa)
   # Press Enter twice for no passphrase
   ```

2. **Get your public key**:
   ```powershell
   # Display your public key
   Get-Content $env:USERPROFILE\.ssh\id_rsa.pub
   # Copy this entire output - you'll need it later
   ```

## Step 1: Sign Up for Oracle Cloud

1. Go to [cloud.oracle.com](https://cloud.oracle.com)
2. Click "Sign Up for Free Tier"
3. Fill in your information:
   - You'll need a credit card (won't be charged)
   - Choose your home region carefully (can't change later)
   - Recommended regions: Phoenix, Ashburn (US), Frankfurt (EU)

## Step 2: Create Your Free VM

1. After signup, go to the Oracle Cloud Console
2. Click the hamburger menu (☰) → Compute → Instances
3. Click "Create Instance"
4. Configure:
   - **Name**: stro-app (or whatever you prefer)
   - **Image**: Ubuntu 22.04
   - **Shape**: Click "Change Shape"
     - Choose "Always Free Eligible"
     - Select ARM-based (Ampere) for 4 OCPU and 24GB RAM FREE!
     - Or AMD for 1 OCPU and 1GB RAM
   - **SSH Keys**: Paste your public key from earlier

5. Click "Create" and wait for instance to be "Running"

## Step 3: Connect from Windows

### Option A: Using Windows Terminal/PowerShell
```powershell
# Note your instance's public IP from the console
# Connect via SSH:
ssh ubuntu@YOUR_INSTANCE_IP

# First time connection will ask to confirm fingerprint - type "yes"
```

### Option B: Using PuTTY (Traditional Windows method)
1. Download PuTTY from putty.org
2. Convert your key to PPK format using PuTTYgen
3. Use PuTTY to connect with your PPK key

## Step 4: Set Up Your App on the Server

Once connected, run these commands:

```bash
# Update the system
sudo apt update && sudo apt upgrade -y

# Install Python, pip, and git
sudo apt install python3-pip python3-venv git nginx -y

# Clone your repository
git clone https://github.com/Harry166/stro.git
cd stro

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Set environment variables
export NEWS_API_KEY="your_news_api_key"
export SECRET_KEY="your_secret_key"
```

## Step 5: Configure Firewall

In Oracle Cloud Console:
1. Go to Networking → Virtual Cloud Networks
2. Click your VCN → Security Lists → Default Security List
3. Add Ingress Rule:
   - Source: 0.0.0.0/0
   - Protocol: TCP
   - Destination Port: 80

On the server:
```bash
# Open firewall on the VM itself
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo netfilter-persistent save
```

## Step 6: Set Up Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/stro

# Paste this configuration:
```

```nginx
server {
    listen 80;
    server_name YOUR_INSTANCE_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/stro /etc/nginx/sites-enabled
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

## Step 7: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/stro.service

# Paste this content:
```

```ini
[Unit]
Description=Stro Stock App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/stro
Environment="PATH=/home/ubuntu/stro/venv/bin"
Environment="NEWS_API_KEY=your_news_api_key"
Environment="SECRET_KEY=your_secret_key"
ExecStart=/home/ubuntu/stro/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start and enable service
sudo systemctl start stro
sudo systemctl enable stro
sudo systemctl status stro
```

## Step 8: Access Your App

1. Open your browser
2. Go to: http://YOUR_INSTANCE_IP
3. Your app should be running!

## Troubleshooting from Windows

```powershell
# Check logs from Windows PowerShell
ssh ubuntu@YOUR_INSTANCE_IP "sudo journalctl -u stro -f"

# Restart the app
ssh ubuntu@YOUR_INSTANCE_IP "sudo systemctl restart stro"

# Check Nginx logs
ssh ubuntu@YOUR_INSTANCE_IP "sudo tail -f /var/log/nginx/error.log"
```

## Tips for Windows Users:

1. **Save your SSH connection**: In Windows Terminal, you can save profiles
2. **Use VS Code**: Install Remote-SSH extension to edit files directly on server
3. **File Transfer**: Use WinSCP or `scp` command in PowerShell
4. **Keep instance active**: Oracle may reclaim idle instances - set up a cron job to keep it active

## Free Resources You Get:
- ✅ 4 ARM CPUs + 24GB RAM (or 1 AMD CPU + 1GB RAM)
- ✅ 200GB Storage
- ✅ 10TB bandwidth/month
- ✅ Static IP address
- ✅ No time limits, truly free forever
- ✅ Can host multiple apps

## Next Steps:
1. Set up a domain name (optional)
2. Add SSL with Let's Encrypt
3. Set up automated backups
4. Monitor your app with Oracle Cloud monitoring
