def QueryValpredios(predios):
    query = """
    REINDEX TABLE """ + predios + """;
    ANALYZE """ + predios + """;
    
    ALTER TABLE """ + predios + """ DROP COLUMN IF EXISTS inconsistencias;    
    ALTER TABLE """ + predios + """ ADD COLUMN IF NOT EXISTS inconsistencias varchar;
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR ESPACIOS INICIO-FIN XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_estado = TRIM(nom_estado) WHERE nom_estado <> TRIM(nom_estado);
    UPDATE """ + mavvial + """ SET nom_mun = TRIM(nom_mun) WHERE nom_mun <> TRIM(nom_mun);
    UPDATE """ + mavvial + """ SET nom_dist = TRIM(nom_dist) WHERE nom_dist <> TRIM(nom_dist);
    UPDATE """ + mavvial + """ SET tipovia = TRIM(tipovia) WHERE tipovia <> TRIM(tipovia);
    UPDATE """ + mavvial + """ SET nombre = TRIM(nombre) WHERE nombre <> TRIM(nombre);
    UPDATE """ + mavvial + """ SET nomb_total = TRIM(nomb_total) WHERE nomb_total <> TRIM(nomb_total);

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR DOBLES ESPACIOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_estado = REPLACE(nom_estado,'  ',' ') WHERE nom_estado LIKE '%  %';
    UPDATE """ + mavvial + """ SET nom_mun = REPLACE(nom_mun,'  ',' ') WHERE nom_mun LIKE '%  %';
    UPDATE """ + mavvial + """ SET nom_dist = REPLACE(nom_dist,'  ',' ') WHERE nom_dist LIKE '%  %';
    UPDATE """ + mavvial + """ SET tipovia = REPLACE(tipovia,'  ',' ') WHERE tipovia LIKE '%  %';
    UPDATE """ + mavvial + """ SET nombre = REPLACE(nombre,'  ',' ') WHERE nombre LIKE '%  %';
    UPDATE """ + mavvial + """ SET nomb_total = REPLACE(nomb_total,'  ',' ') WHERE nomb_total LIKE '%  %';

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX PASAR A MAYUSCULAS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_estado = UPPER(nom_estado) WHERE nom_estado <> UPPER(nom_estado);
    UPDATE """ + mavvial + """ SET nom_mun = UPPER(nom_mun) WHERE nom_mun <> UPPER(nom_mun);
    UPDATE """ + mavvial + """ SET nom_dist = UPPER(nom_dist) WHERE nom_dist <> UPPER(nom_dist);
    UPDATE """ + mavvial + """ SET tipovia = UPPER(tipovia) WHERE tipovia <> UPPER(tipovia);
    UPDATE """ + mavvial + """ SET nombre = UPPER(nombre) WHERE nombre <> UPPER(nombre);
    UPDATE """ + mavvial + """ SET nomb_total = UPPER(nomb_total) WHERE nomb_total <> UPPER(nomb_total);
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX VALIDAR INCONSISTENCIAS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    
    
    DROP TABLE IF EXISTS tabla_temporal;
    """
    #print(query)
    return query
    
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import MultiPoint, Point
from shapely.ops import linemerge

def mv_inconsistencias(engine, mavvial, texto_filtro):

    sql=f"SELECT * FROM {mavvial};"
    mv_mexico = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
    
    #2 id_capa duplicado
    frecuencias = mv_mexico['id_capa'].value_counts().reset_index()
    valor_dict = frecuencias[frecuencias['count'] > 1].set_index('id_capa')['count'].to_dict()
    mv_mexico['inconsistencias'] = mv_mexico.apply(
        lambda row: f"{row['inconsistencias']} - 2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['inconsistencias'] is not None and row['id_capa'] in valor_dict else 
        f"2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['inconsistencias'] is  None and row['id_capa'] in valor_dict else
        row['inconsistencias'],
        axis=1
    )
    
    #3 Campo Nombre es vacio
    idnulo = set(mv_mexico[mv_mexico['nombre'].isna()]['id'].tolist())
    cond1 = mv_mexico['id'].isin(idnulo)
    cond2 = mv_mexico['inconsistencias'].isna()
    mv_mexico.loc[cond1 & ~cond2, 'inconsistencias'] = mv_mexico['inconsistencias'] + " - 3. nombre vacio"
    mv_mexico.loc[cond1 & cond2, 'inconsistencias'] = "3. nombre vacio"
    
    
   #4 Cuadra (generadora) es vacio
    idnulo = set(mv_mexico[mv_mexico['cuadra'].isna()]['id'].tolist())
    cond1 = mv_mexico['id'].isin(idnulo)
    cond2 = mv_mexico['inconsistencias'].isna()
    mv_mexico.loc[cond1 & ~cond2, 'inconsistencias'] = mv_mexico['inconsistencias'] + " - 4. Generadora/altura vacia"
    mv_mexico.loc[cond1 & cond2, 'inconsistencias'] = "4. Generadora/altura vacia"
    
    #5 SALTOS EN PRINCIPAL (NOMBRE) 
    mifiltro=texto_filtro #####AQUI VA EL FILTRO#####
    partes = mifiltro.split(',')
    dep=partes[0]
    prov=partes[1]

    filtro = mv_mexico[(mv_mexico['nom_estado']==dep) & (mv_mexico['nom_mun']==prov)]
    union = filtro[['nom_estado','nom_mun','nom_dist','nomb_total','geom']].dissolve(by=['nom_estado','nom_mun','nom_dist','nomb_total']).reset_index()
    union['geom'] = union['geom'].apply(lambda geom: linemerge(geom) if geom.geom_type == 'MultiLineString' else geom)
    exploded = union.explode(index_parts=False)
    line_counts = exploded.groupby(['nom_estado','nom_mun','nom_dist','nomb_total']).size().reset_index(name='line_count')
    cortadas=line_counts[line_counts['line_count']>1]
    exploded['punto_inicio'] = exploded.geometry.apply(lambda geom: Point(geom.coords[0]) if geom else None)
    exploded['punto_final'] = exploded.geometry.apply(lambda geom: Point(geom.coords[-1]) if geom else None)
    puntos = gpd.GeoSeries(pd.concat([exploded['punto_inicio'], exploded['punto_final']])).value_counts().reset_index(name='conteo')
    puntos.columns = ['punto', 'conteo']
    conteo_gdf = gpd.GeoDataFrame(puntos, geometry='punto')
    multipoint = MultiPoint(conteo_gdf.geometry.tolist())
    gdf_multipoint = gpd.GeoDataFrame(geometry=[multipoint],crs= 'EPSG:4326')
    multi_point = gdf_multipoint.geometry.iloc[0]
    merged = mv_mexico.merge(cortadas, on=['nom_estado', 'nom_mun', 'nom_dist', 'nomb_total'])
    filtered_mv_mexico = merged[merged.geometry.touches(multi_point)]
    idcinco=filtered_mv_mexico['id'].tolist()
    mv_mexico['inconsistencias'] = mv_mexico['inconsistencias'].fillna(pd.NA)
    cond1 = mv_mexico['id'].isin(idcinco)
    cond2 = mv_mexico['inconsistencias'].isna()
    mv_mexico.loc[cond1 & ~cond2, 'inconsistencias'] = mv_mexico['inconsistencias'] + " - 5. Revisar continuidad"
    mv_mexico.loc[cond1 & cond2, 'inconsistencias'] = "5. Revisar continuidad"
    
    #6 Saltos de cuadras
    #mifiltro='ANCASH,HUARAZ' #####AQUI VA EL FILTRO#####
    #partes = mifiltro.split(',')
    #dep=partes[0]
    #prov=partes[1]
    mv_mexico['cuadra'] = pd.to_numeric(mv_mexico['cuadra'])
    agrupados = mv_mexico[(mv_mexico['nom_estado']==dep) & (mv_mexico['nom_mun']==prov)][['nom_estado','nom_mun','nom_dist','nomb_total']].dropna().drop_duplicates().reset_index(drop=True)
    for _,row in agrupados.iterrows():
        filtro = mv_mexico[(mv_mexico['nom_estado']==row[0]) & (mv_mexico['nom_mun']==row[1]) & (mv_mexico['nom_dist']==row[2]) & (mv_mexico['nomb_total']==row[3]) & (mv_mexico['cuadra'].notna())][['id','nom_estado', 'nom_mun', 'nom_dist', 'nomb_total','cuadra','geom']].sort_values(by='cuadra', ascending=True)
        for i,index in enumerate(filtro.index):
            if i < len(filtro) - 1:
                if not mv_mexico.geometry[index].touches(mv_mexico.geometry[filtro.index[i+1]]):
                    for j in range(i+2,len(filtro)):
                        if mv_mexico.geometry[index].touches(mv_mexico.geometry[filtro.index[j]]):
                            #SALTO DE CUADRA
                            if mv_mexico.at[index, 'inconsistencias'] is None:
                                mv_mexico.at[index, 'inconsistencias'] = '6. Salto de generadora'
                            else:
                                mv_mexico.at[index, 'inconsistencias'] = mv_mexico.at[index, 'inconsistencias'] + ' - 6. Salto de generadora'
                            break
                            
    #Llevar informacion
    df_temporal = mv_mexico[['id', 'inconsistencias']]
    df_temporal.to_sql('tabla_temporal', con=engine, index=False, if_exists='replace')