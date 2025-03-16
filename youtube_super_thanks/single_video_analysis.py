import sqlite3
import pandas as pd
import dash
from dash import dcc, html, dash_table, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from config import DATABASE_FILE

# 初始化Dash
app = dash.Dash(__name__, title="影片超級感謝分析")

# 載入特定影片資料
def load_video_data(video_id):
    conn = sqlite3.connect(DATABASE_FILE)
    
    # 讀取影片資訊
    video_info = pd.read_sql_query("SELECT * FROM videos WHERE video_id = ?", conn, params=(video_id,))
    
    if video_info.empty:
        conn.close()
        return None, None
    
    # 讀取該影片的超級感謝資料
    super_thanks = pd.read_sql_query("""
        SELECT * FROM super_thanks
        WHERE video_id = ?
        ORDER BY amount_twd DESC
    """, conn, params=(video_id,))
    
    conn.close()
    
    return video_info.iloc[0], super_thanks

def create_charts(super_thanks):
    figures = {}
    
    # 1. 貨幣分佈圓餅圖
    currency_counts = super_thanks.groupby('currency').size().reset_index(name='counts')
    fig_pie = px.pie(
        currency_counts, 
        names='currency', 
        values='counts',
        title='超級感謝貨幣分佈',
        hole=0.3
    )
    figures['currency_pie'] = fig_pie
    
    # 2. 貨幣金額長條圖
    currency_amounts = super_thanks.groupby('currency')['amount_twd'].sum().reset_index()
    currency_amounts = currency_amounts.sort_values('amount_twd', ascending=False)
    
    fig_bar = px.bar(
        currency_amounts,
        x='currency',
        y='amount_twd',
        title='各貨幣超級感謝總金額 (TWD)',
        labels={'currency': '貨幣', 'amount_twd': '總金額 (TWD)'}
    )
    figures['currency_bar'] = fig_bar
    
    # 3. 評論者排行
    if 'commenter_name' in super_thanks.columns and not super_thanks['commenter_name'].isna().all():
        commenter_stats = super_thanks.groupby('commenter_name').agg({
            'id': 'count',
            'amount_twd': 'sum'
        }).reset_index()
        commenter_stats.columns = ['評論者', '超級感謝次數', '總金額 (TWD)']
        commenter_stats = commenter_stats.sort_values('總金額 (TWD)', ascending=False).head(10)
        
        fig_commenters = px.bar(
            commenter_stats,
            x='評論者',
            y='總金額 (TWD)',
            title='超級感謝金額最高的評論者 (前10名)',
            text='超級感謝次數'
        )
        fig_commenters.update_traces(texttemplate='%{text}', textposition='outside')
        figures['commenters'] = fig_commenters
    
    return figures

app.layout = html.Div([
    html.H1("YouTube 影片超級感謝分析", style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '20px'}),
    
    # 影片ID輸入
    html.Div([
        html.Label("輸入要分析的影片ID:"),
        dcc.Input(
            id='video-id-input',
            type='text',
            value='',
            placeholder='輸入YouTube影片ID',
            style={'width': '300px', 'padding': '8px', 'margin': '10px'}
        ),
        html.Button('分析', id='analyze-button', style={'margin': '10px'})
    ], style={'textAlign': 'center', 'margin': '20px'}),
    
    html.Div(id='video-info'),
    html.Div(id='charts-container'),
    html.Div(id='super-thanks-table')
])

@callback(
    [Output('video-info', 'children'),
     Output('charts-container', 'children'),
     Output('super-thanks-table', 'children')],
    [Input('analyze-button', 'n_clicks')],
    [dash.dependencies.State('video-id-input', 'value')]
)
def update_output(n_clicks, video_id):
    if not n_clicks or not video_id:
        return html.Div(), html.Div(), html.Div()
    
    video_info, super_thanks = load_video_data(video_id)
    
    if video_info is None:
        return html.Div("找不到此影片ID的資料", style={'color': 'red', 'textAlign': 'center'}), html.Div(), html.Div()
    
    # 影片資訊
    info_section = html.Div([
        html.H2(video_info['title'], style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.Div([
            html.Div([
                html.H3("頻道"),
                html.H2(video_info['channel']),
            ], className='stat-card'),
            
            html.Div([
                html.H3("超級感謝總數"),
                html.H2(f"{len(super_thanks)}"),
            ], className='stat-card'),
            
            html.Div([
                html.H3("總金額 (TWD)"),
                html.H2(f"{super_thanks['amount_twd'].sum():,.2f}"),
            ], className='stat-card'),
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px 0'})
    ])
    
    # 生成圖表
    figures = create_charts(super_thanks)
    charts_section = html.Div([
        html.Div([
            html.Div([
                dcc.Graph(figure=figures['currency_pie'])
            ], style={'width': '50%'}),
            
            html.Div([
                dcc.Graph(figure=figures['currency_bar'])
            ], style={'width': '50%'}),
        ], style={'display': 'flex', 'marginBottom': '20px'}),
        
        # 如果有評論者圖表，添加到頁面
        html.Div([
            dcc.Graph(figure=figures['commenters'])
        ], style={'marginBottom': '20px'}) if 'commenters' in figures else html.Div(),
    ])
    
    # 超級感謝表格
    table_section = html.Div([
        html.H2("超級感謝詳細列表", style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '20px'}),
        
        dash_table.DataTable(
            data=super_thanks.to_dict('records'),
            columns=[
                {'name': '貨幣', 'id': 'currency'},
                {'name': '金額', 'id': 'amount', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                {'name': '台幣金額', 'id': 'amount_twd', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                {'name': '評論者', 'id': 'commenter_name'},
                {'name': '日期', 'id': 'comment_date'}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'fontSize': '14px',
                'padding': '8px',
                'textAlign': 'left',
                'whiteSpace': 'normal',
                'height': 'auto',
                'maxWidth': '300px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'
            },
            style_cell_conditional=[
                {'if': {'column_id': 'comment_text'}, 'width': '30%'},
                {'if': {'column_id': 'amount'}, 'textAlign': 'right'},
                {'if': {'column_id': 'amount_twd'}, 'textAlign': 'right'}
            ],
            style_header={
                'backgroundColor': '#f0f0f0',
                'fontWeight': 'bold',
                'fontSize': '16px'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            page_size=15,
            sort_action='native',
            filter_action='native'
        )
    ])
    
    return info_section, charts_section, table_section

if __name__ == "__main__":
    print("啟動單一影片分析網頁 - 請瀏覽 http://127.0.0.1:8050/")
    app.run_server(debug=True)