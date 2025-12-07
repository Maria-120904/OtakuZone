import flet as ft
from services.analytics_service import *

def analytics_dashboard_view(page: ft.Page):
    """Admin Analytics Dashboard with Interactive Charts"""
    
    try:
        # Try to import plotly
        import plotly.graph_objects as go
        import base64
        
        def create_chart_image(fig):
            """Convert plotly figure to base64 image"""
            try:
                img_bytes = fig.to_image(format="png", width=800, height=400)
                img_b64 = base64.b64encode(img_bytes).decode()
                return f"data:image/png;base64,{img_b64}"
            except Exception as e:
                print(f"❌ Chart generation error: {e}")
                return None
        
        plotly_available = True
    except ImportError as e:
        print(f"⚠️ Plotly not available: {e}")
        plotly_available = False

    
    def stat_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=30),
                    ft.Text(str(value), size=32, weight="bold", color="white"),
                ], alignment="spaceBetween"),
                ft.Text(title, size=12, color="#b3b3b3"),
            ], spacing=5),
            bgcolor="#18191A",
            border_radius=12,
            padding=20,
            expand=True,  # Makes each card take 25% width
        )
    
    # Get data
    total_users = get_total_users()
    total_anime = get_total_anime()
    total_episodes = get_total_episodes()
    total_favorites = get_total_favorites()
    
    # 4 equal columns, full width, with spacing
    stats_row = ft.Row([
        stat_card("Total Users", total_users, ft.Icons.PEOPLE, "#4CAF50"),
        stat_card("Total Anime", total_anime, ft.Icons.MOVIE, "#2196F3"),
        stat_card("Total Episodes", total_episodes, ft.Icons.VIDEO_LIBRARY, "#FF9800"),
        stat_card("Total Favorites", total_favorites, ft.Icons.FAVORITE, "#E50914"),
    ], spacing=15, expand=True)

    
    def create_simple_table(title, data, headers):
        """Create a simple data table"""
        if not data:
            return ft.Container(
                content=ft.Text("No data available", color="#b3b3b3", size=14),
                bgcolor="#18191A",
                border_radius=12,
                padding=20,
                expand=True,
            )
        
        rows = []
        for row in data:
            rows.append(
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(str(cell), color="white", size=12)) for cell in row]
                )
            )
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(header, color="white", weight="bold", size=14))
                for header in headers
            ],
            rows=rows,
            border=ft.border.all(1, "#333"),
            border_radius=8,
            bgcolor="#18191A",
            heading_row_color="#222",
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=18, weight="bold", color="white"),
                ft.Divider(color="#E50914", height=1),
                ft.Container(
                    content=table,
                    padding=10,
                ),
            ], spacing=10, scroll="auto"),
            bgcolor="#18191A",
            border_radius=12,
            padding=20,
            expand=True,
        )
    
    # Gender Distribution
    gender_data = get_users_by_gender()
    gender_table = create_simple_table(
        "User Distribution by Gender",
        gender_data,
        ["Gender", "Count"]
    )
    
    # Anime by Category
    category_data = get_anime_by_category()
    category_table = create_simple_table(
        "Anime Distribution by Category",
        category_data,
        ["Category", "Count"]
    )
    
    # Top Favorited Anime
    fav_data = get_most_favorited_anime()
    fav_table = create_simple_table(
        "Top 5 Most Favorited Anime",
        fav_data,
        ["Anime Title", "Favorites"]
    )
    
    # User Growth
    growth_data = get_user_growth_last_7_days()
    growth_table = create_simple_table(
        "User Growth (Last 7 Days)",
        growth_data,
        ["Date", "New Users"]
    )
    
    insights = get_platform_insights()
    
    insights_cards = ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LIGHTBULB, color="#FFD700", size=20),
                ft.Text(insight, size=14, color="white"),
            ], spacing=10),
            bgcolor="#18191A",
            border_radius=8,
            padding=15,
            border=ft.border.all(1, "#E50914")
        )
        for insight in insights
    ], spacing=10)
    
    insights_section = ft.Container(
        content=ft.Column([
            ft.Text("📊 Platform Insights", size=20, weight="bold", color="white"),
            ft.Divider(color="#E50914", height=1),
            insights_cards,
        ], spacing=10),
        bgcolor="#222",
        border_radius=12,
        padding=20,
        expand=True,
    )
    if not plotly_available:
        plotly_notice = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO, color="#FF9800", size=24),
                ft.Column([
                    ft.Text("📊 Interactive Charts Not Available", size=16, weight="bold", color="white"),
                    ft.Text("Install plotly and kaleido for interactive charts:", size=12, color="#b3b3b3"),
                    ft.Text("pip install plotly kaleido", size=12, color="#4CAF50", selectable=True),
                ], spacing=5),
            ], spacing=10),
            bgcolor="#222",
            border_radius=8,
            padding=15,
            border=ft.border.all(2, "#FF9800"),
        )
    else:
        plotly_notice = ft.Container()

    
    return ft.Container(
        content=ft.Column([
            # Title
            ft.Text("Analytics Dashboard", size=24, weight="bold", color="white"),
            ft.Divider(color="#E50914", height=2),
            
            # Plotly Notice
            plotly_notice,
            
            ft.Container(height=10),
            
            # Stat Cards - Full Width (4 equal columns)
            stats_row,
            
            ft.Container(height=20),
            
            # Data Tables - 1 column, 10px spacing
            gender_table,
            ft.Container(height=10),
            category_table,
            ft.Container(height=10),
            fav_table,
            ft.Container(height=10),
            growth_table,
            ft.Container(height=20),
            
            # Insights - Full Width
            insights_section,
        ], spacing=0, scroll="auto", expand=True),
        padding=20,
        expand=True,
    )

if __name__ == "__main__":
    ft.app(target=lambda page: page.add(analytics_dashboard_view(page)))