import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import chardet

# Configurar la página
st.set_page_config(
    page_title="Plataforma Electoral Bolivia 2025",
    page_icon="🇧🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f3c88;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2e4a87;
        border-bottom: 2px solid #1f3c88;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f3c88;
    }
    .department-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal con diseño mejorado
st.markdown('<h1 class="main-header">🇧🇴 Plataforma de Visualización Electoral Bolivia 2025</h1>', unsafe_allow_html=True)
st.markdown("### Sistema Interactivo de Resultados - Primera y Segunda Vuelta")

# Datos geográficos de departamentos de Bolivia
BOLIVIA_DEPARTAMENTOS = {
    'La Paz': {'lat': -16.5, 'lon': -68.15, 'color': '#1f77b4'},
    'Santa Cruz': {'lat': -17.8, 'lon': -63.18, 'color': '#ff7f0e'},
    'Cochabamba': {'lat': -17.4, 'lon': -66.16, 'color': '#2ca02c'},
    'Oruro': {'lat': -17.97, 'lon': -67.12, 'color': '#d62728'},
    'Potosí': {'lat': -19.58, 'lon': -65.75, 'color': '#9467bd'},
    'Chuquisaca': {'lat': -19.0, 'lon': -65.0, 'color': '#8c564b'},
    'Tarija': {'lat': -21.53, 'lon': -64.73, 'color': '#e377c2'},
    'Beni': {'lat': -14.83, 'lon': -64.9, 'color': '#7f7f7f'},
    'Pando': {'lat': -11.03, 'lon': -68.75, 'color': '#bcbd22'}
}

# Lista de los 9 departamentos oficiales
DEPARTAMENTOS_OFICIALES = ['Beni', 'Chuquisaca', 'Cochabamba', 'La Paz', 'Oruro', 'Pando', 'Potosí', 'Santa Cruz', 'Tarija']

def detectar_codificacion(archivo):
    """Detectar automáticamente la codificación del archivo"""
    try:
        with open(archivo, 'rb') as f:
            resultado = chardet.detect(f.read())
            return resultado['encoding']
    except:
        return 'latin-1'

@st.cache_data
def cargar_datos_primera_vuelta():
    """Cargar y procesar datos de la primera vuelta"""
    try:
        codificacion = detectar_codificacion('primera_vuelta.csv')
        codificaciones = [codificacion, 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8']
        
        for cod in codificaciones:
            try:
                df_primera = pd.read_csv('primera_vuelta.csv', encoding=cod)
                
                # Procesar datos de primera vuelta
                partidos_primera = ['AP', 'APB-SUMATE', 'FP', 'LIBRE', 'LYP-ADN', 'MAS-IPSP', 'PDC', 'UNIDAD']
                resultados_primera = {}
                
                for partido in partidos_primera:
                    if partido in df_primera.columns:
                        resultados_primera[partido] = df_primera[partido].sum()
                
                # Análisis por departamento - solo los 9 departamentos oficiales
                departamentos_primera = {}
                for depto in DEPARTAMENTOS_OFICIALES:
                    # Simulación - en producción se haría el mapeo real
                    departamentos_primera[depto] = {
                        'AP': resultados_primera.get('AP', 0) // 9,
                        'PDC': resultados_primera.get('PDC', 0) // 9,
                        'LIBRE': resultados_primera.get('LIBRE', 0) // 9,
                        'MAS-IPSP': resultados_primera.get('MAS-IPSP', 0) // 9
                    }
                
                return resultados_primera, df_primera, departamentos_primera
                
            except Exception:
                continue
        
        return {}, pd.DataFrame(), {}
        
    except Exception as e:
        st.error(f"Error cargando primera vuelta: {e}")
        return {}, pd.DataFrame(), {}

@st.cache_data
def cargar_datos_segunda_vuelta():
    """Cargar y procesar datos de la segunda vuelta"""
    try:
        codificacion = detectar_codificacion('segunda_vuelta.csv')
        codificaciones = [codificacion, 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8']
        
        for cod in codificaciones:
            try:
                df_segunda = pd.read_csv('segunda_vuelta.csv', encoding=cod)
                
                resultados_segunda = {
                    'PDC': df_segunda['PDC'].sum() if 'PDC' in df_segunda.columns else 0,
                    'LIBRE': df_segunda['LIBRE'].sum() if 'LIBRE' in df_segunda.columns else 0
                }
                
                # Análisis por departamento para segunda vuelta - solo los 9 departamentos oficiales
                departamentos_segunda = {}
                if 'NombreDepartamento' in df_segunda.columns:
                    for depto in df_segunda['NombreDepartamento'].unique():
                        if depto in DEPARTAMENTOS_OFICIALES:  # Solo incluir departamentos oficiales
                            depto_data = df_segunda[df_segunda['NombreDepartamento'] == depto]
                            departamentos_segunda[depto] = {
                                'PDC': depto_data['PDC'].sum() if 'PDC' in depto_data.columns else 0,
                                'LIBRE': depto_data['LIBRE'].sum() if 'LIBRE' in depto_data.columns else 0
                            }
                    # Asegurar que todos los departamentos estén presentes
                    for depto in DEPARTAMENTOS_OFICIALES:
                        if depto not in departamentos_segunda:
                            departamentos_segunda[depto] = {
                                'PDC': 0,
                                'LIBRE': 0
                            }
                else:
                    # Simulación si no hay datos de departamento - solo los 9 departamentos
                    for depto in DEPARTAMENTOS_OFICIALES:
                        departamentos_segunda[depto] = {
                            'PDC': resultados_segunda.get('PDC', 0) // 9,
                            'LIBRE': resultados_segunda.get('LIBRE', 0) // 9
                        }
                
                return resultados_segunda, df_segunda, departamentos_segunda
                
            except Exception:
                continue
        
        return {}, pd.DataFrame(), {}
        
    except Exception as e:
        st.error(f"Error cargando segunda vuelta: {e}")
        return {}, pd.DataFrame(), {}

def crear_mapa_departamental(departamentos_data, titulo):
    """Crear mapa cloroplético de Bolivia"""
    deptos = []
    lat = []
    lon = []
    votos_ganador = []
    colores = []
    ganadores = []
    
    for depto, data in departamentos_data.items():
        if depto in BOLIVIA_DEPARTAMENTOS:
            deptos.append(depto)
            lat.append(BOLIVIA_DEPARTAMENTOS[depto]['lat'])
            lon.append(BOLIVIA_DEPARTAMENTOS[depto]['lon'])
            
            pdc_votos = data.get('PDC', 0)
            libre_votos = data.get('LIBRE', 0)
            
            if pdc_votos > libre_votos:
                ganador = 'PDC'
                votos_ganador.append(pdc_votos)
                colores.append('#1f77b4')  # Azul para PDC
            else:
                ganador = 'LIBRE'
                votos_ganador.append(libre_votos)
                colores.append('#ff7f0e')  # Naranja para LIBRE
            
            ganadores.append(ganador)
    
    if deptos:
        fig = px.scatter_mapbox(
            lat=lat,
            lon=lon,
            text=deptos,
            size=votos_ganador,
            color=ganadores,
            color_discrete_map={'PDC': '#1f77b4', 'LIBRE': '#ff7f0e'},
            size_max=30,
            zoom=4,
            height=500,
            title=titulo
        )
        
        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0,"t":30,"l":0,"b":0}
        )
        
        return fig
    return None

def main():
    # Sidebar para navegación
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Bolivia.svg/1200px-Flag_of_Bolivia.svg.png", width=100)
    st.sidebar.title("Navegación")
    
    pagina = st.sidebar.radio(
        "Seleccione una sección:",
        ["🏠 Dashboard Principal", "📊 Análisis Comparativo", "🗺️ Mapa de Resultados", "📈 Evolución Temporal"]
    )
    
    # Cargar datos
    with st.spinner('Cargando datos electorales...'):
        resultados_primera, df_primera, deptos_primera = cargar_datos_primera_vuelta()
        resultados_segunda, df_segunda, deptos_segunda = cargar_datos_segunda_vuelta()
    
    # DASHBOARD PRINCIPAL
    if pagina == "🏠 Dashboard Principal":
        st.markdown('<h2 class="sub-header">Dashboard de Resultados Electorales</h2>', unsafe_allow_html=True)
        
        # Métricas principales en la parte superior
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_mesas = len(df_primera) + len(df_segunda)
            st.metric("📋 Total de Mesas", f"{total_mesas:,}")
        
        with col2:
            if resultados_primera:
                ganador_1ra = max(resultados_primera.items(), key=lambda x: x[1])
                st.metric("🏆 Ganador 1ra Vuelta", ganador_1ra[0], f"{ganador_1ra[1]:,} votos")
        
        with col3:
            if resultados_segunda:
                ganador_2da = 'PDC' if resultados_segunda.get('PDC', 0) > resultados_segunda.get('LIBRE', 0) else 'LIBRE'
                st.metric("🎯 Ganador 2da Vuelta", ganador_2da, f"{max(resultados_segunda.values()):,} votos")
        
        with col4:
            if resultados_primera and resultados_segunda:
                participacion = ((sum(resultados_segunda.values()) / sum(resultados_primera.values())) * 100) if sum(resultados_primera.values()) > 0 else 0
                st.metric("👥 Participación", f"{participacion:.1f}%")
        
        st.markdown("---")
        
        # Visualizaciones principales
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Resultados Primera Vuelta")
            if resultados_primera:
                fig_1ra = px.pie(
                    values=list(resultados_primera.values()),
                    names=list(resultados_primera.keys()),
                    title="Distribución de Votos - Primera Vuelta"
                )
                st.plotly_chart(fig_1ra, use_container_width=True)
            else:
                st.warning("No hay datos de primera vuelta")
        
        with col2:
            st.subheader("🎯 Resultados Segunda Vuelta")
            if resultados_segunda:
                fig_2da = px.pie(
                    values=list(resultados_segunda.values()),
                    names=list(resultados_segunda.keys()),
                    title="Distribución de Votos - Segunda Vuelta"
                )
                st.plotly_chart(fig_2da, use_container_width=True)
            else:
                st.warning("No hay datos de segunda vuelta")
        
        # Mapa rápido
        st.subheader("🗺️ Vista Rápida por Departamento")
        if deptos_segunda:
            mapa_fig = crear_mapa_departamental(deptos_segunda, "Resultados por Departamento - Segunda Vuelta")
            if mapa_fig:
                st.plotly_chart(mapa_fig, use_container_width=True)
    
    # ANÁLISIS COMPARATIVO
    elif pagina == "📊 Análisis Comparativo":
        st.markdown('<h2 class="sub-header">Análisis Comparativo Entre Vueltas</h2>', unsafe_allow_html=True)
        
        if resultados_primera and resultados_segunda:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Evolución PDC vs LIBRE")
                
                # Datos para comparación
                partidos = ['PDC', 'LIBRE']
                votos_1ra = [resultados_primera.get(p, 0) for p in partidos]
                votos_2da = [resultados_segunda.get(p, 0) for p in partidos]
                
                fig_comparativo = go.Figure()
                
                fig_comparativo.add_trace(go.Bar(
                    name='Primera Vuelta',
                    x=partidos,
                    y=votos_1ra,
                    marker_color=['lightblue', 'lightcoral'],
                    text=[f'{v:,}' for v in votos_1ra],
                    textposition='auto'
                ))
                
                fig_comparativo.add_trace(go.Bar(
                    name='Segunda Vuelta',
                    x=partidos,
                    y=votos_2da,
                    marker_color=['blue', 'red'],
                    text=[f'{v:,}' for v in votos_2da],
                    textposition='auto'
                ))
                
                fig_comparativo.update_layout(
                    title='Comparación Directa: Primera vs Segunda Vuelta',
                    barmode='group',
                    xaxis_title='Partidos',
                    yaxis_title='Votos'
                )
                
                st.plotly_chart(fig_comparativo, use_container_width=True)
            
            with col2:
                st.subheader("📊 Análisis de Cambios")
                
                # Calcular cambios
                cambios = []
                for partido in ['PDC', 'LIBRE']:
                    voto_1ra = resultados_primera.get(partido, 0)
                    voto_2da = resultados_segunda.get(partido, 0)
                    cambio = voto_2da - voto_1ra
                    cambio_porc = (cambio / voto_1ra * 100) if voto_1ra > 0 else 0
                    
                    cambios.append({
                        'Partido': partido,
                        '1ra Vuelta': f"{voto_1ra:,}",
                        '2da Vuelta': f"{voto_2da:,}",
                        'Cambio': f"{cambio:+,}",
                        'Tendencia': f"{cambio_porc:+.1f}%"
                    })
                
                df_cambios = pd.DataFrame(cambios)
                st.dataframe(df_cambios, use_container_width=True)
                
                # Análisis de transferencia de votos
                st.subheader("🔄 Transferencia de Votos")
                
                total_1ra = sum(resultados_primera.values())
                total_2da = sum(resultados_segunda.values())
                
                col_met1, col_met2, col_met3 = st.columns(3)
                with col_met1:
                    st.metric("Total 1ra Vuelta", f"{total_1ra:,}")
                with col_met2:
                    st.metric("Total 2da Vuelta", f"{total_2da:,}")
                with col_met3:
                    st.metric("Diferencia", f"{total_2da - total_1ra:+,}")
    
    # MAPA DE RESULTADOS
    elif pagina == "🗺️ Mapa de Resultados":
        st.markdown('<h2 class="sub-header">Representación Geográfica de Resultados</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🗺️ Mapa - Segunda Vuelta")
            if deptos_segunda:
                mapa_2da = crear_mapa_departamental(deptos_segunda, "Resultados por Departamento - Segunda Vuelta")
                if mapa_2da:
                    st.plotly_chart(mapa_2da, use_container_width=True)
            else:
                st.warning("No hay datos geográficos disponibles")
        
        with col2:
            st.subheader("📋 Tabla de Resultados por Departamento")
            if deptos_segunda:
                datos_tabla = []
                for depto in DEPARTAMENTOS_OFICIALES:  # Solo mostrar departamentos oficiales
                    if depto in deptos_segunda:
                        data = deptos_segunda[depto]
                        pdc = data.get('PDC', 0)
                        libre = data.get('LIBRE', 0)
                        total = pdc + libre
                        ganador = 'PDC' if pdc > libre else 'LIBRE'
                        diferencia = abs(pdc - libre)
                        
                        datos_tabla.append({
                            'Departamento': depto,
                            'PDC': f"{pdc:,}",
                            'LIBRE': f"{libre:,}",
                            'Total': f"{total:,}",
                            'Ganador': ganador,
                            'Diferencia': f"{diferencia:,}"
                        })
                
                df_tabla = pd.DataFrame(datos_tabla)
                st.dataframe(df_tabla, use_container_width=True)
        
        # Análisis de patrones regionales
        st.subheader("🔍 Análisis de Patrones Regionales")
        if deptos_segunda:
            patrones_data = []
            for depto in DEPARTAMENTOS_OFICIALES:  # Solo mostrar departamentos oficiales
                if depto in deptos_segunda:
                    data = deptos_segunda[depto]
                    pdc = data.get('PDC', 0)
                    libre = data.get('LIBRE', 0)
                    total = pdc + libre
                    if total > 0:
                        pdc_porc = (pdc / total) * 100
                        patrones_data.append({
                            'Departamento': depto,
                            'PDC (%)': pdc_porc,
                            'LIBRE (%)': 100 - pdc_porc,
                            'Ganador': 'PDC' if pdc > libre else 'LIBRE'
                        })
            
            if patrones_data:
                df_patrones = pd.DataFrame(patrones_data)
                
                fig_patrones = px.bar(
                    df_patrones,
                    x='Departamento',
                    y=['PDC (%)', 'LIBRE (%)'],
                    title='Distribución Porcentual por Departamento',
                    barmode='stack',
                    color_discrete_map={'PDC (%)': '#1f77b4', 'LIBRE (%)': '#ff7f0e'}
                )
                st.plotly_chart(fig_patrones, use_container_width=True)
    
    # EVOLUCIÓN TEMPORAL
    elif pagina == "📈 Evolución Temporal":
        st.markdown('<h2 class="sub-header">Análisis de Evolución y Tendencias</h2>', unsafe_allow_html=True)
        
        if resultados_primera and resultados_segunda:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Evolución de Porcentajes")
                
                # Datos para gráfico de evolución
                partidos = ['PDC', 'LIBRE']
                porcentajes_1ra = [(resultados_primera.get(p, 0) / sum(resultados_primera.values()) * 100) for p in partidos]
                porcentajes_2da = [(resultados_segunda.get(p, 0) / sum(resultados_segunda.values()) * 100) for p in partidos]
                
                fig_evolucion = go.Figure()
                
                for i, partido in enumerate(partidos):
                    fig_evolucion.add_trace(go.Scatter(
                        x=['Primera Vuelta', 'Segunda Vuelta'],
                        y=[porcentajes_1ra[i], porcentajes_2da[i]],
                        mode='lines+markers+text',
                        name=partido,
                        text=[f'{porcentajes_1ra[i]:.1f}%', f'{porcentajes_2da[i]:.1f}%'],
                        textposition='top center',
                        line=dict(width=3)
                    ))
                
                fig_evolucion.update_layout(
                    title='Evolución de Porcentajes Entre Vueltas',
                    xaxis_title='Vuelta Electoral',
                    yaxis_title='Porcentaje (%)',
                    yaxis_range=[0, 60]
                )
                
                st.plotly_chart(fig_evolucion, use_container_width=True)
            
            with col2:
                st.subheader("🎯 Análisis de Competitividad")
                
                # Calcular métricas de competitividad
                pdc_1ra = resultados_primera.get('PDC', 0)
                libre_1ra = resultados_primera.get('LIBRE', 0)
                pdc_2da = resultados_segunda.get('PDC', 0)
                libre_2da = resultados_segunda.get('LIBRE', 0)
                
                diferencia_1ra = abs(pdc_1ra - libre_1ra)
                diferencia_2da = abs(pdc_2da - libre_2da)
                
                col_comp1, col_comp2 = st.columns(2)
                with col_comp1:
                    st.metric("Diferencia 1ra Vuelta", f"{diferencia_1ra:,} votos")
                    margen_1ra = (diferencia_1ra / (pdc_1ra + libre_1ra)) * 100 if (pdc_1ra + libre_1ra) > 0 else 0
                    st.metric("Margen 1ra Vuelta", f"{margen_1ra:.1f}%")
                
                with col_comp2:
                    st.metric("Diferencia 2da Vuelta", f"{diferencia_2da:,} votos")
                    margen_2da = (diferencia_2da / (pdc_2da + libre_2da)) * 100 if (pdc_2da + libre_2da) > 0 else 0
                    st.metric("Margen 2da Vuelta", f"{margen_2da:.1f}%")
                
                # Análisis de tendencia
                st.subheader("📈 Dirección del Cambio")
                if pdc_2da > pdc_1ra and libre_2da < libre_1ra:
                    st.success("✅ PDC ganó terreno, LIBRE perdió apoyo")
                elif pdc_2da < pdc_1ra and libre_2da > libre_1ra:
                    st.success("✅ LIBRE ganó terreno, PDC perdió apoyo")
                else:
                    st.info("📊 Cambio mixto en las tendencias")
    
    # Footer informativo
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🇧🇴 <strong>Plataforma de Visualización Electoral Bolivia 2025</strong></p>
        <p>Desarrollado para análisis de resultados de primera y segunda vuelta | Última actualización: {}</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()