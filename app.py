import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Natura Pricing IA", page_icon="💄", layout="wide")
st.title("📊 Simulador de Elasticidad y Demanda | Natura")
st.markdown("Busca un producto para ver la recomendación de la Inteligencia Artificial y la dispersión histórica de ventas.")


@st.cache_data
def cargar_datos():
    # Cargar las proyecciones de la IA
    df_proj = pd.read_csv('proyecciones_appsheet.csv')
    
    # Cargar y limpiar la base cruda para los gráficos
    df = pd.read_csv('ventas_natura.csv')
    df['Desc Perc'] = df['Desc Perc'].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False)
    df['Desc Perc'] = pd.to_numeric(df['Desc Perc'], errors='coerce') / 100
    df['PrecioLista'] = pd.to_numeric(df['PrecioLista'], errors='coerce')
    df['CantEnviada'] = pd.to_numeric(df['CantEnviada'], errors='coerce')
    df = df.dropna(subset=['Desc Perc', 'PrecioLista', 'CantEnviada'])
    df = df[(df['CantEnviada'] > 0) & (df['PrecioLista'] > 0)]
    
    # Columna para el buscador
    df['SKU_Buscador'] = df['SKU'].astype(str) + " - " + df['NombreProducto']
    
    return df, df_proj

df, df_proj = cargar_datos()


lista_skus = sorted(df['SKU_Buscador'].dropna().unique())
sku_seleccionado = st.selectbox("🔍 Busca o digita el producto:", [""] + lista_skus)

if sku_seleccionado:
    st.divider() # Línea separadora
    
    producto_exacto = sku_seleccionado
    sku_real = producto_exacto.split(" - ")[0] # Sacamos solo el número
    
    df_filtrado = df[df['SKU_Buscador'] == producto_exacto].copy()
    datos_ia = df_proj[df_proj['SKU'].astype(str) == sku_real]
    
   
    if not datos_ia.empty:
        v_reg = datos_ia['Ventas_Proyectadas_Regular'].iloc[0]
        v_cyb = datos_ia['Ventas_Proyectadas_Cyber'].iloc[0]
        elast = datos_ia['Elasticidad_IA'].iloc[0]
        
        # Tarjetas de números
        col1, col2, col3 = st.columns(3)
        col1.metric("Ventas Día Regular (5% Dcto)", f"{v_reg} u.")
        col2.metric("Ventas Cyber (40% Dcto)", f"{v_cyb} u.", f"{round(((v_cyb-v_reg)/v_reg)*100, 1)}% vs Regular")
        col3.metric("Índice de Elasticidad", elast)
        
        # Semáforo de Recomendación
        if elast <= -2.0:
            st.success("🟢 **MUY ELÁSTICO:** Aplica descuento agresivo en Cyber. El volumen extra compensará la caída del precio.")
        elif elast <= -1.0:
            st.warning("🟡 **ELÁSTICO NORMAL:** Reacciona bien al descuento, pero monitorea tu rentabilidad.")
        else:
            st.error("🔴 **INELÁSTICO:** ¡Cuidado! Bajar el precio no aumentará mucho las ventas. Perderás dinero.")
    else:
        st.info("No hay suficientes proyecciones de IA para este producto.")
        
  
    st.subheader("Visualización de Comportamiento")
    df_filtrado['Escenario'] = df_filtrado['CYBER'].apply(lambda x: 'Día Cyber' if x == 1 else 'Día Regular')
    
    fig = px.box(
        df_filtrado,
        x="Desc Perc",              
        y="CantEnviada",            
        points="all",               
        facet_col="Escenario",      
        color="Escenario",          
        height=500,                 
        template="plotly_white",
        color_discrete_map={'Día Regular': '#3498db', 'Día Cyber': '#e74c3c'}
    )
    fig.update_xaxes(tickformat=".0%")
    
    # Mostrar el gráfico en la página web ocupando todo el ancho
    st.plotly_chart(fig, use_container_width=True)