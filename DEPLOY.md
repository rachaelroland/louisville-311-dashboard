# Deploy to Render - Instructions

## ✅ Repository Ready

Your code is now in a GitHub repository:
**https://github.com/rachaelroland/louisville-311-dashboard**

The repo includes `render.yaml` for automatic deployment configuration.

## 🚀 Deploy to Render (2 minutes)

### Option 1: Automatic Blueprint Deployment (Recommended)

1. Visit: **https://dashboard.render.com/blueprints**

2. Click **"New Blueprint Instance"**

3. Connect your GitHub repo:
   - Repository: `rachaelroland/louisville-311-dashboard`
   - Branch: `main`

4. Click **"Apply"**

That's it! Render will automatically:
- Read the `render.yaml` configuration
- Install dependencies from `requirements.txt`
- Deploy the dashboard
- Provide you with a live URL

### Option 2: Manual Web Service Creation

1. Visit: **https://dashboard.render.com/create?type=web**

2. Connect your GitHub account (if not already connected)

3. Select repository: `louisville-311-dashboard`

4. Configure:
   - **Name**: louisville-311-dashboard
   - **Environment**: Python 3
   - **Region**: Oregon (or nearest)
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python dashboard_app.py`
   - **Plan**: Free

5. Add Environment Variables:
   - `PORT` = `10000`
   - `PYTHON_VERSION` = `3.11.0`

6. Click **"Create Web Service"**

## 📊 Access Your Dashboard

After deployment completes (~2-3 minutes), your dashboard will be live at:
```
https://louisville-311-dashboard.onrender.com
```

Or whatever custom URL Render assigns.

## 🔧 Automatic Updates

Any push to the `main` branch will automatically trigger a new deployment!

```bash
# Make changes locally
git add -A
git commit -m "Update dashboard"
git push origin main

# Render will automatically redeploy
```

## 📝 Current Configuration

From `render.yaml`:
```yaml
services:
  - type: web
    name: louisville-311-dashboard
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python dashboard_app.py
```

## ⚠️ Important Notes

### Data File Issue
The dashboard currently loads data from:
```python
CSV_PATH = Path("/Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed/311_processed_with_nlp.csv")
```

**This path won't exist on Render!** You need to either:

1. **Include sample data** in the repo (recommended for demo)
2. **Load from URL** - Host the CSV somewhere and fetch it
3. **Use smaller dataset** - Sample 10,000 records for faster loading

### Quick Fix Option 1: Sample Data

```bash
# Create sample dataset (10,000 records)
cd /Users/rachael/Documents/projects/rachaelroland/pipelines/pipelines/311/data/processed
head -1 311_processed_with_nlp.csv > sample_311_data.csv
tail -n +2 311_processed_with_nlp.csv | head -10000 >> sample_311_data.csv

# Copy to dashboard repo
cp sample_311_data.csv /Users/rachael/Downloads/311_nlp_analysis_report/

# Update dashboard_app.py to use local file
# Change line ~19 to:
# CSV_PATH = CURRENT_DIR / "sample_311_data.csv"

# Commit and push
cd /Users/rachael/Downloads/311_nlp_analysis_report
git add sample_311_data.csv dashboard_app.py
git commit -m "Add sample data for deployment"
git push origin main
```

### Quick Fix Option 2: Mock Data

Update `dashboard_app.py` to generate mock data if file not found:

```python
if not CSV_PATH.exists():
    # Generate mock data for demo
    print("Using mock data for demo")
    df = pd.DataFrame({
        'sentiment': ['negative']*45000 + ['neutral']*55000,
        'urgency_level': ['low']*70000 + ['medium']*20000 + ['high']*10000,
        'service_name': ['Illegal Dumping']*20000 + ['Street Lighting']*15000 + ['Waste Collection']*10000,
        # ... etc
    })
```

## 🎯 Next Steps

1. **Fix data loading** (choose option above)
2. **Deploy to Render** (use Option 1 or 2)
3. **Test the dashboard** at the provided URL
4. **Share with stakeholders**

## 🆘 Troubleshooting

**Build fails?**
- Check Render build logs
- Verify `requirements.txt` dependencies
- Check Python version compatibility

**App crashes?**
- Check Render application logs
- Verify data file path issue is fixed
- Test locally first: `PORT=10000 python dashboard_app.py`

**Can't access dashboard?**
- Wait 2-3 minutes for initial deploy
- Check Render dashboard for service status
- Verify no build/runtime errors in logs
