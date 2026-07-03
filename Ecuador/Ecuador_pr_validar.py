def QueryValpredios(predios):
    query = """
    REINDEX TABLE """ + predios + """;
    ANALYZE """ + predios + """;
    
    ALTER TABLE """ + predios + """ DROP COLUMN IF EXISTS inconsistencias;    
    ALTER TABLE """ + predios + """ ADD COLUMN IF NOT EXISTS inconsistencias varchar;
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR ESPACIOS INICIO-FIN XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_dep = TRIM(nom_dep) WHERE nom_dep <> TRIM(nom_dep);
    UPDATE """ + mavvial + """ SET nom_prov = TRIM(nom_prov) WHERE nom_prov <> TRIM(nom_prov);
    UPDATE """ + mavvial + """ SET nom_dist = TRIM(nom_dist) WHERE nom_dist <> TRIM(nom_dist);
    UPDATE """ + mavvial + """ SET tipovia = TRIM(tipovia) WHERE tipovia <> TRIM(tipovia);
    UPDATE """ + mavvial + """ SET nombre = TRIM(nombre) WHERE nombre <> TRIM(nombre);
    UPDATE """ + mavvial + """ SET nomb_total = TRIM(nomb_total) WHERE nomb_total <> TRIM(nomb_total);

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR DOBLES ESPACIOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_dep = REPLACE(nom_dep,'  ',' ') WHERE nom_dep LIKE '%  %';
    UPDATE """ + mavvial + """ SET nom_prov = REPLACE(nom_prov,'  ',' ') WHERE nom_prov LIKE '%  %';
    UPDATE """ + mavvial + """ SET nom_dist = REPLACE(nom_dist,'  ',' ') WHERE nom_dist LIKE '%  %';
    UPDATE """ + mavvial + """ SET tipovia = REPLACE(tipovia,'  ',' ') WHERE tipovia LIKE '%  %';
    UPDATE """ + mavvial + """ SET nombre = REPLACE(nombre,'  ',' ') WHERE nombre LIKE '%  %';
    UPDATE """ + mavvial + """ SET nomb_total = REPLACE(nomb_total,'  ',' ') WHERE nomb_total LIKE '%  %';

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX PASAR A MAYUSCULAS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_dep = UPPER(nom_dep) WHERE nom_dep <> UPPER(nom_dep);
    UPDATE """ + mavvial + """ SET nom_prov = UPPER(nom_prov) WHERE nom_prov <> UPPER(nom_prov);
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
    mv_peru = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
    
    #2 id_capa duplicado
    frecuencias = mv_peru['id_capa'].value_counts().reset_index()
    valor_dict = frecuencias[frecuencias['count'] > 1].set_index('id_capa')['count'].to_dict()
    mv_peru['inconsistencias'] = mv_peru.apply(
        lambda row: f"{row['inconsistencias']} - 2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['inconsistencias'] is not None and row['id_capa'] in valor_dict else 
        f"2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['inconsistencias'] is  None and row['id_capa'] in valor_dict else
        row['inconsistencias'],
        axis=1
    )
    
    #3 Campo Nombre es vacio
    idnulo = set(mv_peru[mv_peru['nombre'].isna()]['id'].tolist())
    cond1 = mv_peru['id'].isin(idnulo)
    cond2 = mv_peru['inconsistencias'].isna()
    mv_peru.loc[cond1 & ~cond2, 'inconsistencias'] = mv_peru['inconsistencias'] + " - 3. nombre vacio"
    mv_peru.loc[cond1 & cond2, 'inconsistencias'] = "3. nombre vacio"
    
    
   #4 Cuadra (generadora) es vacio
    idnulo = set(mv_peru[mv_peru['cuadra'].isna()]['id'].tolist())
    cond1 = mv_peru['id'].isin(idnulo)
    cond2 = mv_peru['inconsistencias'].isna()
    mv_peru.loc[cond1 & ~cond2, 'inconsistencias'] = mv_peru['inconsistencias'] + " - 4. Generadora/altura vacia"
    mv_peru.loc[cond1 & cond2, 'inconsistencias'] = "4. Generadora/altura vacia"
    
    #5 SALTOS EN PRINCIPAL (NOMBRE) 
    mifiltro=texto_filtro #####AQUI VA EL FILTRO#####
    partes = mifiltro.split(',')
    dep=partes[0]
    prov=partes[1]

    filtro = mv_peru[(mv_peru['nom_dep']==dep) & (mv_peru['nom_prov']==prov)]
    union = filtro[['nom_dep','nom_prov','nom_dist','nomb_total','geom']].dissolve(by=['nom_dep','nom_prov','nom_dist','nomb_total']).reset_index()
    union['geom'] = union['geom'].apply(lambda geom: linemerge(geom) if geom.geom_type == 'MultiLineString' else geom)
    exploded = union.explode(index_parts=False)
    line_counts = exploded.groupby(['nom_dep','nom_prov','nom_dist','nomb_total']).size().reset_index(name='line_count')
    cortadas=line_counts[line_counts['line_count']>1]
    exploded['punto_inicio'] = exploded.geometry.apply(lambda geom: Point(geom.coords[0]) if geom else None)
    exploded['punto_final'] = exploded.geometry.apply(lambda geom: Point(geom.coords[-1]) if geom else None)
    puntos = gpd.GeoSeries(pd.concat([exploded['punto_inicio'], exploded['punto_final']])).value_counts().reset_index(name='conteo')
    puntos.columns = ['punto', 'conteo']
    conteo_gdf = gpd.GeoDataFrame(puntos, geometry='punto')
    multipoint = MultiPoint(conteo_gdf.geometry.tolist())
    gdf_multipoint = gpd.GeoDataFrame(geometry=[multipoint],crs= 'EPSG:4326')
    multi_point = gdf_multipoint.geometry.iloc[0]
    merged = mv_peru.merge(cortadas, on=['nom_dep', 'nom_prov', 'nom_dist', 'nomb_total'])
    filtered_mv_peru = merged[merged.geometry.touches(multi_point)]
    idcinco=filtered_mv_peru['id'].tolist()
    mv_peru['inconsistencias'] = mv_peru['inconsistencias'].fillna(pd.NA)
    cond1 = mv_peru['id'].isin(idcinco)
    cond2 = mv_peru['inconsistencias'].isna()
    mv_peru.loc[cond1 & ~cond2, 'inconsistencias'] = mv_peru['inconsistencias'] + " - 5. Revisar continuidad"
    mv_peru.loc[cond1 & cond2, 'inconsistencias'] = "5. Revisar continuidad"
    
    #6 Saltos de cuadras
    #mifiltro='ANCASH,HUARAZ' #####AQUI VA EL FILTRO#####
    #partes = mifiltro.split(',')
    #dep=partes[0]
    #prov=partes[1]
    mv_peru['cuadra'] = pd.to_numeric(mv_peru['cuadra'])
    agrupados = mv_peru[(mv_peru['nom_dep']==dep) & (mv_peru['nom_prov']==prov)][['nom_dep','nom_prov','nom_dist','nomb_total']].dropna().drop_duplicates().reset_index(drop=True)
    for _,row in agrupados.iterrows():
        filtro = mv_peru[(mv_peru['nom_dep']==row[0]) & (mv_peru['nom_prov']==row[1]) & (mv_peru['nom_dist']==row[2]) & (mv_peru['nomb_total']==row[3]) & (mv_peru['cuadra'].notna())][['id','nom_dep', 'nom_prov', 'nom_dist', 'nomb_total','cuadra','geom']].sort_values(by='cuadra', ascending=True)
        for i,index in enumerate(filtro.index):
            if i < len(filtro) - 1:
                if not mv_peru.geometry[index].touches(mv_peru.geometry[filtro.index[i+1]]):
                    for j in range(i+2,len(filtro)):
                        if mv_peru.geometry[index].touches(mv_peru.geometry[filtro.index[j]]):
                            #SALTO DE CUADRA
                            if mv_peru.at[index, 'inconsistencias'] is None:
                                mv_peru.at[index, 'inconsistencias'] = '6. Salto de generadora'
                            else:
                                mv_peru.at[index, 'inconsistencias'] = mv_peru.at[index, 'inconsistencias'] + ' - 6. Salto de generadora'
                            break
                            
    #Llevar informacion
    df_temporal = mv_peru[['id', 'inconsistencias']]
    df_temporal.to_sql('tabla_temporal', con=engine, index=False, if_exists='replace')