import os
import sqlite3
import pandas as pd
import dash
from dash import dcc, html, dash_table, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from config import DATABASE_FILE

os.makedirs('assets', exist_ok=True)

# 初始化Dash
app = dash.Dash(
    __name__, 
    title="YouTube 超級感謝統計",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

def load_data():
    conn = sqlite3.connect(DATABASE_FILE)
    
    # 影片資料
    videos_df = pd.read_sql_query("SELECT * FROM videos", conn)
    
    # 超級感謝資料
    super_thanks_df = pd.read_sql_query("""
        SELECT s.*, v.title as video_title, v.channel 
        FROM super_thanks s
        JOIN videos v ON s.video_id = v.video_id
    """, conn)
    
    # 貨幣匯率資料
    currency_df = pd.read_sql_query("SELECT * FROM currency_rates", conn)
    
    conn.close()
    
    return videos_df, super_thanks_df, currency_df

# 載入特定影片資料
def load_video_data(video_id):
    conn = sqlite3.connect(DATABASE_FILE)
    
    video_info = pd.read_sql_query("SELECT * FROM videos WHERE video_id = ?", conn, params=(video_id,))
    if video_info.empty:
        conn.close()
        return None, None
    
    super_thanks = pd.read_sql_query("""
        SELECT * FROM super_thanks
        WHERE video_id = ?
        ORDER BY amount_twd DESC
    """, conn, params=(video_id,))
    
    conn.close()
    
    return video_info.iloc[0], super_thanks

# 創建總覽圖表
def create_overview_figures(videos_df, super_thanks_df, currency_df):
    figures = {}
    
    # 1. 影片超級感謝數量分佈
    video_counts = super_thanks_df.groupby(['video_id', 'video_title', 'channel']).size().reset_index(name='counts')
    video_counts = video_counts.sort_values('counts', ascending=False).head(10)
    
    # 莫蘭迪色系
    morandi_colors = ['#e6c9c9', '#a5b5c1', '#b8c5ba', '#c6b5a5', '#bfb6ca', '#d1cfcd', '#b6cad4', '#8a9eae', '#cad4c8', '#e5d6d6']
    
    fig_video_counts = px.bar(
        video_counts,
        x='video_title',
        y='counts',
        color='channel',
        title='各影片超級感謝數量 (前10名)',
        labels={'video_title': '影片標題', 'counts': '超級感謝數量', 'channel': '頻道'},
        color_discrete_sequence=morandi_colors
    )
    fig_video_counts.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#5c5c5c'
    )
    figures['video_counts'] = fig_video_counts
    
    # 2. 影片超級感謝金額分佈 (TWD)
    video_amount = super_thanks_df.groupby(['video_id', 'video_title', 'channel'])['amount_twd'].sum().reset_index()
    video_amount = video_amount.sort_values('amount_twd', ascending=False).head(10)
    
    fig_video_amount = px.bar(
        video_amount,
        x='video_title',
        y='amount_twd',
        color='channel',
        title='各影片超級感謝總金額 (TWD) (前10名)',
        labels={'video_title': '影片標題', 'amount_twd': '總金額 (TWD)', 'channel': '頻道'}
    )
    fig_video_amount.update_layout(xaxis_tickangle=-45)
    figures['video_amount'] = fig_video_amount
    
    # 3. 貨幣分佈
    currency_dist = super_thanks_df.groupby('currency').size().reset_index(name='counts')
    currency_dist = currency_dist.sort_values('counts', ascending=False)
    
    fig_currency_dist = px.pie(
        currency_dist,
        names='currency',
        values='counts',
        title='超級感謝貨幣分佈',
        hole=0.3
    )
    figures['currency_dist'] = fig_currency_dist
    
    # 4. 各貨幣金額統計
    currency_amount = super_thanks_df.groupby('currency')['amount_twd'].sum().reset_index()
    currency_amount = currency_amount.sort_values('amount_twd', ascending=False)
    
    fig_currency_amount = px.bar(
        currency_amount,
        x='currency',
        y='amount_twd',
        title='各貨幣超級感謝總金額 (TWD)',
        labels={'currency': '貨幣', 'amount_twd': '總金額 (TWD)'}
    )
    figures['currency_amount'] = fig_currency_amount
    
    # 5. 頻道統計 
    channel_stats = super_thanks_df.groupby('channel').agg({
        'id': 'count',
        'amount_twd': 'sum'
    }).reset_index()
    
    channel_stats.columns = ['頻道', '超級感謝數量', '總金額 (TWD)']
    channel_stats = channel_stats.sort_values('總金額 (TWD)', ascending=False)
    
    # 頻道金額分佈
    fig_channel = px.bar(
        channel_stats,
        x='頻道',
        y='總金額 (TWD)',
        title='各頻道超級感謝總金額',
        text='超級感謝數量'
    )
    fig_channel.update_traces(texttemplate='%{text}', textposition='outside')
    figures['channel_dist'] = fig_channel
    
    return figures, channel_stats

# 創建單一影片圖表
def create_video_charts(super_thanks):
    figures = {}
    
    # 1. 貨幣分佈圓餅圖
    currency_counts = super_thanks.groupby('currency').size().reset_index(name='counts')
    if not currency_counts.empty:
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
    if not currency_amounts.empty:
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
        
        if not commenter_stats.empty:
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

# 導航欄
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("總覽", href="/")),
        dbc.NavItem(dbc.NavLink("單一影片分析", href="/video")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("關於", header=True),
                dbc.DropdownMenuItem("說明", href="/about"),
            ],
            nav=True,
            in_navbar=True,
            label="更多",
        ),
    ],
    brand="YouTube 超級感謝統計儀表板",
    brand_href="/",
    color="#8d7b6c",  # 深咖啡色
    dark=True,
)

# 網頁最上面標題部分樣式
card_header_style = {"background-color": "#c6b5a5", "color": "#000000"}  # 咖啡色背景，黑色文字

# 頁面內容
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    videos_df, super_thanks_df, currency_df = load_data()
    
    # 總覽頁面
    if pathname == "/":
        figures, channel_stats = create_overview_figures(videos_df, super_thanks_df, currency_df)
        
        total_videos = len(videos_df)
        total_super_thanks = len(super_thanks_df)
        total_amount = super_thanks_df['amount_twd'].sum()
        
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("總影片數", className="card-title"),
                            html.H2(f"{total_videos}", className="card-text text-primary"),
                        ])
                    ], className="mb-4 shadow")
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("總超級感謝數", className="card-title"),
                            html.H2(f"{total_super_thanks}", className="card-text text-primary"),
                        ])
                    ], className="mb-4 shadow")
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("總金額 (TWD)", className="card-title"),
                            html.H2(f"{total_amount:,.2f}", className="card-text text-primary"),
                        ])
                    ], className="mb-4 shadow")
                ], width=4),
            ], className="mt-4"),
            
            # 圖表
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=figures['video_amount'])
                        ])
                    ], className="mb-4 shadow")
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=figures['currency_amount'])
                        ])
                    ], className="mb-4 shadow")
                ], width=6),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=figures['channel_dist'])
                        ])
                    ], className="mb-4 shadow")
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=figures['currency_dist'])
                        ])
                    ], className="mb-4 shadow")
                ], width=6),
            ]),
            
            # 頻道統計表格
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("頻道統計摘要")),
                        dbc.CardBody([
                            dash_table.DataTable(
                                data=channel_stats.to_dict('records'),
                                columns=[{'name': col, 'id': col} for col in channel_stats.columns],
                                style_table={'overflowX': 'auto'},
                                style_cell={
                                    'fontSize': '14px',
                                    'padding': '8px',
                                    'textAlign': 'center'
                                },
                                style_header={
                                    'backgroundColor': '#f0f0f0',
                                    'fontWeight': 'bold',
                                    'fontSize': '16px',
                                    'color': '#000000'
                                },
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
                                ],
                                page_size=10,
                                sort_action='native'
                            )
                        ])
                    ], className="mb-4 shadow")
                ], width=12),
            ]),
            
            # 影片列表
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("全部影片列表")),
                        dbc.CardBody([
                            dash_table.DataTable(
                                id='videos-table',
                                data=videos_df.to_dict('records'),
                                columns=[
                                    {'name': '影片ID', 'id': 'video_id'},
                                    {'name': '標題', 'id': 'title'},
                                    {'name': '頻道', 'id': 'channel'},
                                    {'name': '抓取日期', 'id': 'scrape_date'}
                                ],
                                style_table={'overflowX': 'auto'},
                                style_cell={
                                    'fontSize': '14px',
                                    'padding': '8px',
                                    'textAlign': 'left',
                                    'whiteSpace': 'normal',
                                    'height': 'auto'
                                },
                                style_header={
                                    'backgroundColor': '#f0f0f0',
                                    'fontWeight': 'bold',
                                    'fontSize': '16px',
                                    'color': '#000000'
                                },
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
                                ],
                                page_size=10,
                                sort_action='native'
                            ),
                            html.Div([
                                dbc.Button("查看詳細", id="view-details-btn", color="primary", className="mt-3"),
                                html.Div(id="video-details-output")
                            ])
                        ])
                    ], className="mb-4 shadow")
                ], width=12),
            ]),
        ])
    
    # 單一影片分析頁面
    elif pathname == "/video":
        return html.Div([
            dbc.Card([
                dbc.CardHeader(html.H4("影片超級感謝分析")),
                dbc.CardBody([
                    # 影片ID輸入
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("輸入要分析的影片ID:"),
                            dbc.Input(
                                id='video-id-input',
                                type='text',
                                placeholder='輸入YouTube影片ID',
                            ),
                            dbc.Button('分析', id='analyze-button', color="primary", className="mt-2")
                        ], width={"size": 6, "offset": 3}),
                    ], className="mb-4"),
                ])
            ], className="mb-4 shadow"),
            
            html.Div(id='video-info'),
            html.Div(id='charts-container'),
            html.Div(id='super-thanks-table')
        ])
    
    # 關於頁面
    elif pathname == "/about":
        return html.Div([
            dbc.Card([
                dbc.CardHeader(html.H4("關於此工具")),
                dbc.CardBody([
                    html.P("YouTube 超級感謝統計儀表板是一個用於分析YouTub影片中超級感謝的工具。"),
                    html.P("本工具能夠抓取YouTube影片的超級感謝資料，並提供各種統計分析和視覺化圖表。"),
                    html.H5("主要功能："),
                    html.Ul([
                        html.Li("抓取YouTube影片的超級感謝資料"),
                        html.Li("按照不同貨幣統計超級感謝金額"),
                        html.Li("分析各頻道/影片的超級感謝分佈"),
                        html.Li("提供視覺化圖表展示分析結果"),
                    ])
                ])
            ], className="mb-4 shadow")
        ])
    
    # 預設返回首頁
    return html.Div([
        html.H1("404 - 找不到頁面!"),
        html.Hr(),
        html.P(f"路徑 '{pathname}' 不存在..."),
        dbc.Button("返回首頁", href="/", color="primary")
    ])

# 處理單一影片分析
@app.callback(
    [Output('video-info', 'children'),
     Output('charts-container', 'children'),
     Output('super-thanks-table', 'children')],
    [Input('analyze-button', 'n_clicks')],
    [dash.dependencies.State('video-id-input', 'value')]
)
def update_video_analysis(n_clicks, video_id):
    if not n_clicks or not video_id:
        return html.Div(), html.Div(), html.Div()
    
    video_info, super_thanks = load_video_data(video_id)
    
    if video_info is None:
        return dbc.Alert("找不到此影片ID的資料", color="danger"), html.Div(), html.Div()
    
    # 影片資訊
    info_section = dbc.Card([
        dbc.CardHeader(html.H4(video_info['title'])),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("頻道", className="card-title"),
                            html.H2(video_info['channel'], className="card-text text-primary"),
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("超級感謝總數", className="card-title"),
                            html.H2(f"{len(super_thanks)}", className="card-text text-primary"),
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("總金額 (TWD)", className="card-title"),
                            html.H2(f"{super_thanks['amount_twd'].sum():,.2f}", className="card-text text-primary"),
                        ])
                    ])
                ], width=4),
            ])
        ])
    ], className="mb-4 shadow")
    
    # 生成圖表
    figures = create_video_charts(super_thanks)
    
    if not figures:
        charts_section = dbc.Alert("此影片沒有足夠的數據來生成圖表", color="warning")
    else:
        charts_section = html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=figures['currency_pie']) if 'currency_pie' in figures else html.Div()
                        ])
                    ], className="mb-4 shadow")
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=figures['currency_bar']) if 'currency_bar' in figures else html.Div()
                        ])
                    ], className="mb-4 shadow")
                ], width=6),
            ]),
            
            # 如果有評論者圖表，添加到頁面
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=figures['commenters'])
                        ])
                    ], className="mb-4 shadow")
                ], width=12),
            ]) if 'commenters' in figures else html.Div(),
        ])
    
    # 超級感謝表格
    table_section = dbc.Card([
        dbc.CardHeader(html.H4("超級感謝詳細列表")),
        dbc.CardBody([
            dash_table.DataTable(
                data=super_thanks.to_dict('records'),
                columns=[
                    {'name': '貨幣', 'id': 'currency'},
                    {'name': '金額', 'id': 'amount', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                    {'name': '台幣金額', 'id': 'amount_twd', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                    {'name': '評論者', 'id': 'commenter_name'},
                ],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'fontSize': '14px',
                    'padding': '8px',
                    'textAlign': 'right',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'maxWidth': '300px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis'
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'commenter_name'}, 'textAlign': 'left'}
                ],
                style_header={
                    'backgroundColor': '#f0f0f0',
                    'fontWeight': 'bold',
                    'fontSize': '16px',
                    'color': '#000000'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                page_size=15,
                sort_action='native'
            )
        ])
    ], className="mb-4 shadow")
    
    return info_section, charts_section, table_section

@app.callback(
    Output('video-details-output', 'children'),
    [Input('view-details-btn', 'n_clicks')],
    [dash.dependencies.State('videos-table', 'selected_rows'),
     dash.dependencies.State('videos-table', 'data')]
)
def view_selected_video(n_clicks, selected_rows, data):
    if not n_clicks or not selected_rows:
        return html.Div()
    
    selected_row = selected_rows[0]
    video_id = data[selected_row]['video_id']
    
    return dcc.Location(pathname=f"/video?id={video_id}", id="redirect-to-video")

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,
    dbc.Container(id="page-content", className="pt-4", fluid=True),
])

if __name__ == "__main__":
    print("啟動網頁儀表板 - 請訪問 http://127.0.0.1:8050/")
    app.run_server(debug=True)