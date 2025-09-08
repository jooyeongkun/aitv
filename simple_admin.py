from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import sqlite3
import uvicorn

app = FastAPI(title="Travel Admin Dashboard")

def get_db_connection():
    conn = sqlite3.connect('travel_consultation.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", response_class=HTMLResponse)
async def admin_home():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get counts
    cursor.execute("SELECT COUNT(*) as count FROM packages")
    package_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM hotels")
    hotel_count = cursor.fetchone()['count']
    
    # Get all packages
    cursor.execute("SELECT * FROM packages ORDER BY created_at DESC")
    packages = cursor.fetchall()
    
    # Get all hotels
    cursor.execute("SELECT * FROM hotels ORDER BY created_at DESC")
    hotels = cursor.fetchall()
    
    conn.close()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Travel Admin Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .stats {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .stat-box {{ background: #f0f0f0; padding: 20px; border-radius: 8px; }}
            .section {{ margin-bottom: 40px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            h1, h2 {{ color: #333; }}
        </style>
    </head>
    <body>
        <h1>Travel Admin Dashboard</h1>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Packages</h3>
                <p><strong>{package_count}</strong> total packages</p>
            </div>
            <div class="stat-box">
                <h3>Hotels</h3>
                <p><strong>{hotel_count}</strong> total hotels</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Travel Packages</h2>
            <table>
                <tr>
                    <th>ID</th><th>Name</th><th>Destination</th><th>Price</th><th>Duration</th><th>Category</th>
                </tr>
    """
    
    for package in packages:
        html += f"""
                <tr>
                    <td>{package['id']}</td>
                    <td>{package['name']}</td>
                    <td>{package['destination']}</td>
                    <td>{package['price']:,} KRW</td>
                    <td>{package['duration']} days</td>
                    <td>{package['category']}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
        
        <div class="section">
            <h2>Hotels</h2>
            <table>
                <tr>
                    <th>ID</th><th>Name</th><th>City</th><th>Rating</th><th>Price/Night</th><th>Address</th>
                </tr>
    """
    
    for hotel in hotels:
        html += f"""
                <tr>
                    <td>{hotel['id']}</td>
                    <td>{hotel['name']}</td>
                    <td>{hotel['city']}</td>
                    <td>{hotel['star_rating']} stars</td>
                    <td>{hotel['price_per_night']:,} KRW</td>
                    <td>{hotel['address']}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
    </body>
    </html>
    """
    
    return html

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)