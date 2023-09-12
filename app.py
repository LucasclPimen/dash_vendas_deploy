############ Bibliotecas de dashboard ###########
import dash 
from dash.dependencies import Input, Output
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

############ Bibliotecas de manipulação de dados ###########
import pandas as pd
import numpy as np

load_figure_template('minty')
############ Bibliotecas de construção de gráficos ###########
import plotly.express as px
import plotly.graph_objects as go

# ============== INGESTÃO DE DADOS ============== #
data = pd.read_csv('supermarket_sales.csv')
data['Date'] = pd.to_datetime(data['Date'])

# ============== CRIÇÃO DO APP E LAYOUT ============== #
app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])
server = app.server

app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.H2('PIMEN', style={'font-family':'Zaptron','font-size':'40px', 'margin-left':'10px','margin-top':'5px'}),
                html.Hr(),
                html.H5("Cidades:", style={"font-size": '15px'}),
                #Checklist
                dcc.Checklist(
                    options = data['City'].value_counts().index,
                    value = data['City'].value_counts().index,
                    id = 'check_city',
                    inline = True,
                    inputStyle={'margin-right':'5px', 'margin-left':'15px'}
                ),
                #Criando um Radio items
                html.H5('Variável de Análise', style = {'font-size':'15px', 'margin-top':'30px'}),
                dcc.RadioItems(
                    options = ['gross income','Rating'],
                    value = 'gross income',
                    id = 'main_variable',
                    inline = False,
                    inputStyle={'margin-top':'5px', 'margin-left':'15px'},
                ),
                    
            ],style = {'height':'90vh', 'margin':'10px', 'padding': '20px'})
            
        ], sm =2),
        dbc.Col([
            dbc.Row([
                dbc.Col([dcc.Graph(id = 'city_fig')],sm=4),
                dbc.Col([dcc.Graph(id = 'gen_fig')],sm=4),
                dbc.Col([dcc.Graph(id = 'pay_fig'),],sm=4),          
                
            ]),

            dbc.Row([dcc.Graph(id = 'income_per_date_fig')]),
            dbc.Row([
                dbc.Col([dcc.Graph(id = 'income_per_product_fig')]) 
            ]),
        ], sm = 10)
    ])
])


# ============== CALLBACKS ============== #
# No caso deste projeto, retornam os gráficos de acordo com as configurações do Checklist e dos RsdioItems
@app.callback(
    Output('city_fig', 'figure'),
    Output('gen_fig', 'figure'),
    Output('pay_fig', 'figure'),
    Output('income_per_date_fig','figure'),
    Output('income_per_product_fig','figure'),
    Input('check_city','value'),  # cities
    Input('main_variable','value') #variable
)

def update_output(city, variable):
    #depende do tipo de variável em questão 
    operation = np.sum if variable == 'gross income' else np.mean

    #filtrando o conjunto de dados:

    filtered_data = data[data['City'].isin(city)]  #contém as informações das cidades selecionadas no checklist

    data_city = filtered_data.groupby('City')[variable].apply(operation).to_frame().reset_index()
    data_gender = filtered_data.groupby(['Gender', 'City'])[variable].apply(operation).to_frame().reset_index()
    data_city_payment = filtered_data.groupby('Payment')[variable].apply(operation).to_frame().reset_index()
    df_income_date = filtered_data.groupby('Date')[variable].apply(operation).to_frame().reset_index()
    df_product_income = filtered_data.groupby(['City','Product line'])[variable].apply(operation).to_frame().reset_index()
    #Após aplicar a operação, há uma Series. Entretanto, o plotly express precisa de um DataFrame para a construção dos gráficos e, além disso,
    # precisa de colunas que mostrem o que vai estar no eixo x e no eixo y SEM CONSIDERAR o índice
    fig1 = px.bar(x='City',y=variable, color ='City', data_frame=data_city)
    fig2 = px.bar(x='Gender',y=variable,color = 'City', data_frame=data_gender,barmode = 'group')
    fig3 = px.bar(x=variable,y='Payment', data_frame=data_city_payment,color ='Payment', orientation ='h')
    fig4 = px.bar(x='Date',y=variable, data_frame=df_income_date)
    fig5 = px.bar(x=variable, y = "Product line", data_frame=df_product_income, color = 'City',orientation = 'h', barmode = 'group')
    
    for fig in [fig1,fig2,fig3,fig4]:
         fig.update_layout(margin = dict(l=5,r=0,t=25,b=20), height = 200, template ='minty')
    
    fig5.update_layout(margin = dict(l=0,r=0,t=20,b=20), height = 500, template = 'minty')

    return fig1, fig2, fig3, fig4, fig5 

# ============== RUN SERVER ============== #

if __name__ =='__main__':
      app.run_server(debug=False)

      