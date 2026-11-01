import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar la página de Streamlit
st.set_page_config(page_title="Dashboard de Análisis de Ventas", layout="wide")

st.title("📊 Dashboard de Análisis de Ventas y Rentabilidad")
st.markdown("Este dashboard interactivo presenta un análisis detallado del rendimiento de ventas, distribución regional, rentabilidad y productos críticos.")

# Función para cargar los datos de manera eficiente con caché
@st.cache_data
def load_data():
    # Recuerda cambiar esta ruta por la de tu archivo local si lo descargas
    file_path = '/content/drive/MyDrive/Colab Notebooks/SalidaVentas.xlsx'
    return pd.read_excel(file_path)

try:
    df = load_data()
    st.sidebar.success("¡Datos cargados correctamente!")
except Exception as e:
    st.sidebar.error(f"Error al cargar los datos: {e}")
    st.stop()

# Crear pestañas para organizar los análisis de forma limpia
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Distribuciones Generales", 
    "🗺️ Análisis Regional de Ventas", 
    "💰 Rentabilidad por Región y Estado", 
    "⚠️ Productos con Pérdidas"
])

sns.set_theme(style="whitegrid")

# --- PESTAÑA 1: DISTRIBUCIONES ---
with tab1:
    st.header("Distribución de Ventas y Ganancias")
    st.markdown("Visualiza la frecuencia y dispersión de las variables de Ventas (`Sales`) y Ganancias (`Profit`).")
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Distribución de Sales
    sns.histplot(df['Sales'], kde=True, ax=axes[0], color='skyblue', bins=50)
    axes[0].set_title('Distribución de Ventas (Sales)')
    axes[0].set_xlabel('Sales')
    axes[0].set_ylabel('Frecuencia')
    
    # Distribución de Profit
    sns.histplot(df['Profit'], kde=True, ax=axes[1], color='salmon', bins=50)
    axes[1].set_title('Distribución de Ganancias (Profit)')
    axes[1].set_xlabel('Profit')
    axes[1].set_ylabel('Frecuencia')
    
    st.pyplot(fig)

# --- PESTAÑA 2: ANÁLISIS REGIONAL DE VENTAS ---
with tab2:
    st.header("Ventas Regionales y Detalle por Estado")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Proporción de Ventas por Región")
        ventas_por_region = df.groupby('Region')['Sales'].sum().reset_index()
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.pie(
            ventas_por_region['Sales'],
            labels=ventas_por_region['Region'],
            autopct='%1.1f%%',
            startangle=140,
            colors=['#5dade2', '#f5b041', '#58d68d', '#ec7063']
        )
        ax1.set_title('Total de Ventas por Región')
        st.pyplot(fig1)
        
    with col2:
        st.subheader("Filtro Detallado: Ventas por Estado en Región West")
        df_west = df[df['Region'] == 'West']
        ventas_estado_west = df_west.groupby('State')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)
        
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        sns.barplot(
            x='Sales',
            y='State',
            data=ventas_estado_west,
            palette='viridis',
            hue='State',
            legend=False,
            ax=ax2
        )
        ax2.set_title('Ventas por Estado (Región West)')
        ax2.set_xlabel('Total Ventas')
        ax2.set_ylabel('Estado')
        st.pyplot(fig2)

# --- PESTAÑA 3: RENTABILIDAD DINÁMICA ---
with tab3:
    st.header("Análisis de Ganancias (Profit)")
    
    # Análisis Dinámico de Región Líder
    profit_por_region = df.groupby('Region')['Profit'].sum().reset_index()
    region_mayor_profit = profit_por_region.sort_values(by='Profit', ascending=False).iloc[0]['Region']
    
    st.info(f"💡 La región detectada con mayor ganancia acumulada es: **{region_mayor_profit}**")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Total de Ganancias por Región")
        fig3, ax3 = plt.subplots(figsize=(6, 6))
        ax3.pie(
            profit_por_region['Profit'],
            labels=profit_por_region['Region'],
            autopct='%1.1f%%',
            startangle=140,
            colors=['#5dade2', '#f5b041', '#58d68d', '#ec7063']
        )
        ax3.set_title('Proporción de Profit por Región')
        st.pyplot(fig3)
        
    with col4:
        st.subheader(f"Ganancias por Estado en la Región {region_mayor_profit}")
        df_top_region = df[df['Region'] == region_mayor_profit]
        profit_estado_top = df_top_region.groupby('State')['Profit'].sum().reset_index().sort_values(by='Profit', ascending=False)
        
        fig4, ax4 = plt.subplots(figsize=(8, 6))
        sns.barplot(
            x='Profit',
            y='State',
            data=profit_estado_top,
            palette='coolwarm',
            hue='State',
            legend=False,
            ax=ax4
        )
        ax4.set_title(f'Ganancias por Estado ({region_mayor_profit})')
        ax4.set_xlabel('Total Ganancias')
        ax4.set_ylabel('Estado')
        st.pyplot(fig4)

# --- PESTAÑA 4: PRODUCTOS CON PÉRDIDAS ---
with tab4:
    st.header("Alerta: Productos con mayores pérdidas acumuladas")
    st.warning("A continuación se listan los 5 productos que acumulan la mayor cantidad de pérdidas netas (valores de profit más negativos).")
    
    productos_profit = df.groupby('Product Name')['Profit'].sum().reset_index()
    peores_productos = productos_profit[productos_profit['Profit'] < 0].sort_values(by='Profit', ascending=True).head(5)
    
    # Mostrar métricas destacadas del peor producto
    peor_producto = peores_productos.iloc[0]
    st.metric(
        label=f"Peor Producto: {peor_producto['Product Name']}", 
        value=f"${peor_producto['Profit']:,.2f}",
        delta="Pérdida Máxima"
    )
    
    # Presentar tabla en formato interactivo y estilizado
    st.dataframe(peores_productos.style.format({"Profit": "${:,.2f}"}), use_container_width=True)
