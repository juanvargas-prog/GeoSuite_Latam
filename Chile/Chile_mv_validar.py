def Chile_QueryValMavvial(mavvial,placas):
    query = """
    REINDEX TABLE """ + mavvial + """;
    ANALYZE """ + mavvial + """;
    
    ALTER TABLE """ + mavvial + """ DROP COLUMN IF EXISTS incidencia;  
    ALTER TABLE """ + mavvial + """ ADD COLUMN IF NOT EXISTS incidencia varchar;
    
    ALTER TABLE """ + mavvial + """ DROP COLUMN IF EXISTS rangopar;    
    ALTER TABLE """ + mavvial + """ ADD COLUMN IF NOT EXISTS rangopar varchar;
    
    ALTER TABLE """ + mavvial + """ DROP COLUMN IF EXISTS rangoimpar;    
    ALTER TABLE """ + mavvial + """ ADD COLUMN IF NOT EXISTS rangoimpar varchar;
      
    ALTER TABLE """ + mavvial + """ ADD COLUMN IF NOT EXISTS atipico varchar;
    ALTER TABLE """ + placas + """ ADD COLUMN IF NOT EXISTS atipico varchar;
          
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX PASAR A MAYUSCULAS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_reg = UPPER(nom_reg) WHERE nom_reg <> UPPER(nom_reg);
    UPDATE """ + mavvial + """ SET nom_prov = UPPER(nom_prov) WHERE nom_prov <> UPPER(nom_prov);
    UPDATE """ + mavvial + """ SET nom_com = UPPER(nom_com) WHERE nom_com <> UPPER(nom_com);
    UPDATE """ + mavvial + """ SET nomvia = UPPER(nomvia) WHERE nomvia <> UPPER(nomvia);
    UPDATE """ + mavvial + """ SET nomvtotal = UPPER(nomvtotal) WHERE nomvtotal <> UPPER(nomvtotal);
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX REEMPLAZAR SIMBOLOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/  
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX REEMPLAZAR SIMBOLOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/  
    UPDATE """ + mavvial + """ SET nom_reg = regexp_replace(nom_reg, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_reg ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + mavvial + """ SET nom_prov = regexp_replace(nom_prov, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_prov ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + mavvial + """ SET nom_com = regexp_replace(nom_com, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_com ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';

    UPDATE """ + mavvial + """ SET nomvia = regexp_replace(nomvia, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nomvia ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]'
    AND nomvia != 'S/N';
    
    UPDATE """ + mavvial + """ SET nomvtotal = regexp_replace(nomvtotal, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nomvtotal ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]'
    AND nomvtotal != 'S/N';
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR ESPACIOS INICIO-FIN XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_reg = TRIM(nom_reg) WHERE nom_reg <> TRIM(nom_reg);
    UPDATE """ + mavvial + """ SET nom_prov = TRIM(nom_prov) WHERE nom_prov <> TRIM(nom_prov);
    UPDATE """ + mavvial + """ SET nom_com = TRIM(nom_com) WHERE nom_com <> TRIM(nom_com);
    UPDATE """ + mavvial + """ SET nomvia = TRIM(nomvia) WHERE nomvia <> TRIM(nomvia);
    UPDATE """ + mavvial + """ SET nomvtotal = TRIM(nomvtotal) WHERE nomvtotal <> TRIM(nomvtotal);

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR DOBLES ESPACIOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_reg = REPLACE(nom_reg,'  ',' ') WHERE nom_reg LIKE '%  %';
    UPDATE """ + mavvial + """ SET nom_prov = REPLACE(nom_prov,'  ',' ') WHERE nom_prov LIKE '%  %';
    UPDATE """ + mavvial + """ SET nom_com = REPLACE(nom_com,'  ',' ') WHERE nom_com LIKE '%  %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'  ',' ') WHERE nomvia LIKE '%  %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'  ',' ') WHERE nomvtotal LIKE '%  %';
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX VALIDAR incidencia XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/

    DROP TABLE IF EXISTS tabla_temporal;
    """
    #print(query)
    return query
    
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import MultiPoint, Point, LineString, MultiLineString
from shapely.ops import linemerge
from math import atan2, degrees, radians
from shapely.affinity import rotate
from shapely.ops import substring
from rtree import index as indexx
import re
import networkx as nx

def Chile_mv_incidencia(mv_chile, placas_chile, texto_filtro, key,idx):
            
    if key ==1 :

        # 1. Validar registro con caracteres
        id_excp = list(mv_chile.loc[mv_chile['exclusion'].str.contains(r'\[1\]', na=False),'id'])
        # Expresión regular para caracteres especiales
        simbolos = r'[|!"#@$%&/()¿¡¨{}\[\]._:,;+\-*=/¬°]'

        # Función para marcar la inconsistencia si hay caracteres especiales en alguna columna específica
        def marcar_simbolos(row):
            if row['nomvia'] != 'S/N':
                columnas = ['nom_reg', 'nom_prov', 'tipovia', 'nomvia', 'nomvtotal']
                for col in columnas:
                    if pd.notna(row[col]) and re.search(simbolos, row[col]) and (row['id'] not in id_excp):
                        return '1. Validar registro con caracteres - '
            return None

        # Aplicar la función para marcar incidencia
        mv_chile['incidencia'] = mv_chile.apply(marcar_simbolos, axis=1)
        
    if key == 2:
        #2 id_capa duplicado
        frecuencias = mv_chile['id_capa'].value_counts().reset_index()
        valor_dict = frecuencias[frecuencias['count'] > 1].set_index('id_capa')['count'].to_dict()
        id_excp = list(mv_chile.loc[mv_chile['exclusion'].str.contains(r'\[2\]', na=False),'id'])
        mv_chile['incidencia'] = mv_chile.apply(
            lambda row: f"{row['incidencia']} - 2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is not None and row['id_capa'] in valor_dict and row['id'] not in id_excp else 
            f"2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is  None and row['id_capa'] in valor_dict and row['id'] not in id_excp else
            row['incidencia'],
            axis=1
        )

    if key == 3:        
        #3 Campo nomvia es vacio
        filtro = mv_chile[(mv_chile['cod_prov']==texto_filtro)].copy()

        # Función para obtener el punto inicial de una geometría, sea LineString o MultiLineString
        def get_start_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, simplemente tomamos el primer punto
                return Point(geom.coords[0])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el primer punto del primer LineString
                first_line = list(geom.geoms)[0]
                return Point(first_line.coords[0])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None

        # Función para obtener el punto final de una geometría, sea LineString o MultiLineString
        def get_end_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, tomamos el último punto
                return Point(geom.coords[-1])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el último punto del último LineString
                last_line = list(geom.geoms)[-1]
                return Point(last_line.coords[-1])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None

        # Definir función para calcular el azimuth entre dos puntos
        def calculate_azimuth(start, end):
            dx = end.x - start.x
            dy = end.y - start.y

            angle_rad = atan2(dx, dy)
            angle_deg = degrees(angle_rad)

            # Normalizar a rango 0–360
            if angle_deg < 0:
                angle_deg += 360
            
            return angle_deg
            #return atan2(dy, dx)

        # Aplicar función a cada geometría (asumiendo que son LineStrings)
        filtro['punto_inicio'] = filtro['geom'].apply(get_start_point)
        filtro['punto_fin'] = filtro['geom'].apply(get_end_point)
        filtro['orientacion'] = filtro.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        #Agregarlongitud
        filtro['longitud'] = filtro.to_crs(epsg=3857).geometry.length
        #-----------------------------------------

        # Unir el GeoDataFrame consigo mismo para comparar segmentos cercanos o que se intersectan
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
        # Filtrar donde no sean la misma línea
        joined = joined[joined['id_1'] != joined['id_2']]

        # Calcular diferencias de orientación
        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        # Clasificar las relaciones en 'Paralelas', 'Perpendiculares', o 'No son paralelas ni perpendiculares'
        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < 30:
                return 'Paralelas'
            elif 30 < diferencia_orientacion < 150:
                return 'Perpendiculares'
            elif  150< diferencia_orientacion < 210:
                return 'Paralelas invertidas'
            elif  210< diferencia_orientacion < 360:
                return 'Perpendiculares'
            else:
                return 'No son paralelas ni perpendiculares'

        joined['relacion'] = joined['diferencia_orientacion'].apply(clasificar_relacion)

        joined['generadora_1'] = pd.to_numeric(joined['generadora_1'])
        joined['generadora_2'] = pd.to_numeric(joined['generadora_2'])

        #Necesarioparalo nuevo------------
        joined.loc[(joined['punto_inicio_1'].intersects(joined['punto_inicio_2'])|(joined['punto_inicio_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'inicio'
        joined.loc[(joined['punto_fin_1'].intersects(joined['punto_inicio_2'])|(joined['punto_fin_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'fin'
        counts = joined.groupby('id_1').agg(
            total=('id_1', 'size'),
            inicio_count=('conexion', lambda x: (x.str.contains('inicio')).sum()),
            final_count=('conexion', lambda x: (x.str.contains('fin')).sum())
        ).reset_index()
        joined.reset_index(drop=False,inplace=True)
        joined = joined.merge(counts[['id_1', 'inicio_count','final_count']], on='id_1', how='left')
        joined.loc[joined['conexion']=='fin','validacion_call']=joined['inicio_count']
        joined.loc[joined['conexion']=='inicio','validacion_call']=joined['final_count']
        joined.set_index('index', inplace=True)
        #----------------------

        paralelas_nombres = joined[(joined['relacion'] == 'Paralelas') | (joined['relacion'] == 'Paralelas invertidas')]
        SN=paralelas_nombres[((paralelas_nombres['nomvia_1'].isna()) | (paralelas_nombres['nomvia_1'].str.contains('S/N',na=False))) & (paralelas_nombres['longitud_1'] > 15)]

        id_par_sn = SN[(SN['nomvia_2'].notna()) & ~(SN['nomvia_2'].str.contains('S/N',na=False))].index.unique()
        id_cll=joined[(joined['nomvia_1'].isna() | joined['nomvia_1'].str.contains('S/N',na=False)) & (joined['validacion_call']==0)].index.unique()
        idnulo=set(id_par_sn)-set(id_cll)

        cond1 = mv_chile.index.isin(idnulo)
        cond2 = mv_chile['incidencia'].isna()
        cond3 = mv_chile['exclusion'].str.contains(r'\[3\]', na=False)
        mv_chile.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_chile['incidencia'] + " - 3. nomvia vacio"
        mv_chile.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "3. nomvia vacio"

    if key == 4:    
        #4 generadora (generadora) es vacio

        filtro = mv_chile[(mv_chile['cod_prov']==texto_filtro)].copy()

        # Función para obtener el punto inicial de una geometría, sea LineString o MultiLineString
        def get_start_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, simplemente tomamos el primer punto
                return Point(geom.coords[0])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el primer punto del primer LineString
                first_line = list(geom.geoms)[0]
                return Point(first_line.coords[0])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None

        # Función para obtener el punto final de una geometría, sea LineString o MultiLineString
        def get_end_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, tomamos el último punto
                return Point(geom.coords[-1])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el último punto del último LineString
                last_line = list(geom.geoms)[-1]
                return Point(last_line.coords[-1])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None
            
        def calculate_azimuth(start, end):
            dx = end.x - start.x
            dy = end.y - start.y

            angle_rad = atan2(dx, dy)
            angle_deg = degrees(angle_rad)

            # Normalizar a rango 0–360
            if angle_deg < 0:
                angle_deg += 360
            
            return angle_deg

        # Aplicar función a cada geometría (asumiendo que son LineStrings)
        filtro['punto_inicio'] = filtro['geom'].apply(get_start_point)
        filtro['punto_fin'] = filtro['geom'].apply(get_end_point)
        filtro['orientacion'] = filtro.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        #Agregarlongitud
        filtro['longitud'] = filtro.to_crs(epsg=3857).geometry.length
        #-----------------------------------------

        # Unir el GeoDataFrame consigo mismo para comparar segmentos cercanos o que se intersectan
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
        # Filtrar donde no sean la misma línea
        joined = joined[joined['id_1'] != joined['id_2']]

        # Calcular diferencias de orientación
        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        # Clasificar las relaciones en 'Paralelas', 'Perpendiculares', o 'No son paralelas ni perpendiculares'
        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < 30:
                return 'Paralelas'
            elif 30 < diferencia_orientacion < 150:
                return 'Perpendiculares'
            elif  150< diferencia_orientacion < 210:
                return 'Paralelas invertidas'
            elif  210< diferencia_orientacion < 360:
                return 'Perpendiculares'
            else:
                return 'No son paralelas ni perpendiculares'

        joined['relacion'] = joined['diferencia_orientacion'].apply(clasificar_relacion)
        joined['generadora_1'] = pd.to_numeric(joined['generadora_1'])
        joined['generadora_2'] = pd.to_numeric(joined['generadora_2'])

        #Necesarioparalo nuevo------------
        joined.loc[(joined['punto_inicio_1'].intersects(joined['punto_inicio_2'])|(joined['punto_inicio_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'inicio'
        joined.loc[(joined['punto_fin_1'].intersects(joined['punto_inicio_2'])|(joined['punto_fin_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'fin'
        counts = joined.groupby('id_1').agg(
            total=('id_1', 'size'),
            inicio_count=('conexion', lambda x: (x.str.contains('inicio')).sum()),
            final_count=('conexion', lambda x: (x.str.contains('fin')).sum())
        ).reset_index()
        joined.reset_index(drop=False,inplace=True)
        joined = joined.merge(counts[['id_1', 'inicio_count','final_count']], on='id_1', how='left')
        joined.loc[joined['conexion']=='fin','validacion_call']=joined['inicio_count']
        joined.loc[joined['conexion']=='inicio','validacion_call']=joined['final_count']
        joined.set_index('index', inplace=True)


        paralelas_generadora = joined[(joined['relacion'] == 'Paralelas') | (joined['relacion'] == 'Paralelas invertidas')]
        SG=paralelas_generadora[(paralelas_generadora['generadora_1'].isna()) & (paralelas_generadora['longitud_1']>15) ]
        
        id_par_sg = SG[(SG['generadora_2'].notna())].index.unique()
        id_cll=joined[(joined['generadora_1'].isna()) & (joined['validacion_call']==0)].index.unique()
        generadoranulo=set(id_par_sg)-set(id_cll)

        cond1 = mv_chile.index.isin(generadoranulo)
        cond2 = mv_chile['incidencia'].isna()
        cond3 = mv_chile['exclusion'].str.contains(r'\[4\]', na=False)
        mv_chile.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_chile['incidencia'] + " - 4. Generadora vacia"
        mv_chile.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "4. Generadora vacia"

    if key == 5:     
        #5 MV REPETIDAS

        #P1
        copia_malla=mv_chile[(mv_chile['cod_prov']==texto_filtro) &(~mv_chile['nomvtotal'].str.contains('S/N', na=False))].dropna(subset=['cod_reg', 'cod_prov','cod_com','nomvtotal','generadora']).reset_index(drop=False).set_index(['cod_reg','cod_prov','cod_com','nomvtotal','generadora','costado']).sort_index()
        #Agregarlongitud
        copia_malla['longitud'] = copia_malla.to_crs(epsg=3857).geometry.length
        mallamas15=copia_malla[copia_malla['longitud']>15]
        repeated_indices = mallamas15.index.value_counts()
        repeated_indices = repeated_indices[repeated_indices > 1].index
        ind_rep_p1 = list(copia_malla[copia_malla.index.isin(repeated_indices)]['index'])

        #P2
        filtro = mv_chile[(mv_chile['cod_prov']==texto_filtro) & (~mv_chile['nomvtotal'].str.contains('S/N', na=False))].copy()

        # Función para obtener el punto inicial de una geometría, sea LineString o MultiLineString
        def get_start_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, simplemente tomamos el primer punto
                return Point(geom.coords[0])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el primer punto del primer LineString
                first_line = list(geom.geoms)[0]
                return Point(first_line.coords[0])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None

        # Función para obtener el punto final de una geometría, sea LineString o MultiLineString
        def get_end_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, tomamos el último punto
                return Point(geom.coords[-1])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el último punto del último LineString
                last_line = list(geom.geoms)[-1]
                return Point(last_line.coords[-1])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None

        # Definir función para calcular el azimuth entre dos puntos
        def calculate_azimuth(start, end):
            dx = end.x - start.x
            dy = end.y - start.y

            angle_rad = atan2(dx, dy)
            angle_deg = degrees(angle_rad)

            # Normalizar a rango 0–360
            if angle_deg < 0:
                angle_deg += 360
            
            return angle_deg

        # Aplicar función a cada geometría (asumiendo que son LineStrings)
        filtro['punto_inicio'] = filtro['geom'].apply(get_start_point)
        filtro['punto_fin'] = filtro['geom'].apply(get_end_point)
        filtro['orientacion'] = filtro.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        #Agregarlongitud
        filtro['longitud'] = filtro.to_crs(epsg=3857).geometry.length
        #-----------------------------------------

        # Unir el GeoDataFrame consigo mismo para comparar segmentos cercanos o que se intersectan
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
        # Filtrar donde no sean la misma línea
        joined = joined[joined['id_1'] != joined['id_2']]

        # Calcular diferencias de orientación
        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        # Clasificar las relaciones en 'Paralelas', 'Perpendiculares', o 'No son paralelas ni perpendiculares'
        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < 30:
                return 'Paralelas'
            elif 30 < diferencia_orientacion < 150:
                return 'Perpendiculares'
            elif  150< diferencia_orientacion < 210:
                return 'Paralelas invertidas'
            elif  210< diferencia_orientacion < 360:
                return 'Perpendiculares'
            else:
                return 'No son paralelas ni perpendiculares'

        joined['relacion'] = joined['diferencia_orientacion'].apply(clasificar_relacion)
        joined['generadora_1'] = pd.to_numeric(joined['generadora_1'])
        joined['generadora_2'] = pd.to_numeric(joined['generadora_2'])

        #Necesarioparalo nuevo
        joined.loc[(joined['punto_inicio_1'].intersects(joined['punto_inicio_2'])|(joined['punto_inicio_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'inicio'
        joined.loc[(joined['punto_fin_1'].intersects(joined['punto_inicio_2'])|(joined['punto_fin_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'fin'
        counts = joined.groupby('id_1').agg(
            total=('id_1', 'size'),
            inicio_count=('conexion', lambda x: (x.str.contains('inicio')).sum()),
            final_count=('conexion', lambda x: (x.str.contains('fin')).sum())
        ).reset_index()
        joined.reset_index(drop=False,inplace=True)
        joined = joined.merge(counts[['id_1', 'inicio_count','final_count']], on='id_1', how='left')
        joined.loc[joined['conexion']=='fin','validacion_t']=joined['final_count']
        joined.loc[joined['conexion']=='inicio','validacion_t']=joined['inicio_count']
        #------------------------------------
        joined.set_index('index', inplace=True)

        #vias_rep = joined[(joined['nomvtotal_1'] == joined['nomvtotal_2']) & (joined['generadora_1'] == joined['generadora_2'])].copy()
        vias_rep = joined[(joined['nomvtotal_1'] == joined['nomvtotal_2']) & (joined['generadora_1'] == joined['generadora_2']) & (joined['costado_1'] == joined['costado_2'])].copy()
        vias_rep_con_t=vias_rep[(vias_rep['validacion_t']==2)]

        ind_rep_p2=vias_rep_con_t.index
        ind_rep = set(ind_rep_p1)-set(ind_rep_p2)

        cond1 = mv_chile.index.isin(ind_rep)
        cond2 = mv_chile['incidencia'].isna()
        cond3 = mv_chile['exclusion'].str.contains(r'\[5\]', na=False)
        mv_chile.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_chile['incidencia'] + " - 5. Via repetida"
        mv_chile.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "5. Via repetida"

    if key == 6:     
        #6 SALTOS EN PRINCIPAL (nomvia)
        filtro = mv_chile[(mv_chile['cod_prov']==texto_filtro) & (mv_chile['nomvia'].notna()) & (~mv_chile['nomvia'].str.contains('S/N', na=False)) ].copy()
        #Agrupar por cod_prov y nomvia
        union = filtro[['cod_prov','nomvia','geom']].dissolve(by=['cod_prov','nomvia'])
        union['geom'] = union['geom'].apply(lambda geom: linemerge(geom) if geom.geom_type == 'MultiLineString' else geom)
        #explottar para obtener linestring 
        exploded = union.explode(index_parts=False)
        #mirar cuales aparecen mas de una vez
        duplicated_indices = exploded.index[exploded.index.duplicated(keep=False)].unique()
        #obtenemos solo los repetidos
        repetidos = exploded[exploded.index.isin(duplicated_indices)].copy()
        #----------
        repetidos['punto_inicio1'] = repetidos.geometry.apply(lambda geom: Point(geom.coords[0]) if geom else None)
        repetidos['punto_final1'] = repetidos.geometry.apply(lambda geom: Point(geom.coords[-1]) if geom else None)
        repetidos.reset_index(drop=False,inplace=True)
        
        #----------
        # Cargar el GeoDataFrame de las líneas 
        repetidos['grupo']=None
        for a in duplicated_indices:
            gdf = repetidos[(repetidos['cod_prov']==a[0]) & (repetidos['nomvia']==a[1])]
            # Crear un grafo vacío
            G = nx.Graph()

            # Iterar sobre cada par de líneas para ver si están conectadas
            for i in  gdf.itertuples(index=True):
                for j in  gdf.itertuples(index=True):
                    if i.Index != j.Index:  # Evitar comparaciones consigo mismo
                        # Verificar si las líneas tocan o se cruzan
                        if i.geom.intersects(j.geom):
                            # Añadir una arista entre las líneas en el grafo
                            G.add_edge(i.Index, j.Index)

            # Ahora G tiene un grafo con conexiones entre las líneas
            # Encontrar las componentes conexas (grupos de líneas conectadas)
            componentes_conexas = list(nx.connected_components(G))

            # Asignar el grupo a cada línea según su componente conexo
            for i, componente in enumerate(componentes_conexas):
                for indice in componente:
                    repetidos.at[indice, 'grupo'] = i+1
                    gdf.at[indice, 'grupo'] = i+1
            minifiltro = gdf[gdf['grupo'].isna()]
            
            for k in  minifiltro.itertuples(index=True):
                repetidos.at[k.Index, 'grupo'] = len(componentes_conexas)+1
                #gdf.loc[k.Index, 'grupo'] = len(componentes_conexas)
                componentes_conexas.append({k.Index})
        #-------------------
        #Cada linea con su punto inicial o final
        puntos_sep = pd.concat([repetidos.reset_index(drop=False)[['cod_prov','nomvia','punto_inicio1','geom','grupo']].rename(columns={'punto_inicio1': 'punto'}), repetidos.reset_index(drop=False)[['cod_prov','nomvia','punto_final1','geom','grupo']].rename(columns={'punto_final1': 'punto'})], axis=0)
        #Cuantas lineas tocan cada punto
        agrupados = puntos_sep.groupby(['cod_prov', 'nomvia','punto','grupo']).size().reset_index(name='count')
        #Obtener solo puntos extremos o sea solo puntos 1
        unos=agrupados[agrupados['count']==1][['cod_prov', 'nomvia','punto','grupo']]
            #2. rotondas trayecto cerrados
            #3 o +. Uniones de vias como callejones o salidas de puentes o de autopistas grandes
        #----------------------
        #Grupos existentes con extremos  
        group_counts = unos.groupby(['cod_prov', 'nomvia'])['grupo'].nunique()

        # Filtrar solo aquellas combinaciones donde coddist y nomvvtotal tiene multiples grupos (quitar trayectorias cerradas)
        combinations_with_multiple_groups = group_counts[group_counts > 1].index

        # Filtrar el DataFrame original para obtener las combinaciones y sus ggrupos con sus puntos extremos
        filtro_uno_mas_grupos = unos[unos.set_index(['cod_prov', 'nomvia']).index.isin(combinations_with_multiple_groups)]

        #Puntos agrupados (en un solo campo) por cod_prov,nomvia y grupo (externos)
        puntos_agrupados = filtro_uno_mas_grupos.groupby(['cod_prov', 'nomvia', 'grupo']).agg(
            puntos=('punto',list)  # Crear una lista de puntos
        ).reset_index()
        #obtener de repetidos los trayectos que resultan de los filtros anteriores (lineas)
        ultimo_filtro=repetidos[repetidos.set_index(['cod_prov','nomvia','grupo']).index.isin(puntos_agrupados.set_index(['cod_prov','nomvia','grupo']).index)][['cod_prov','nomvia','geom','grupo']]  
        #Unir todas las geometrias que se tocan en una (Multilinestring) para comparar la cercania de una geometria con todos los puntos de los otros grupos
        ultima_union = ultimo_filtro.dissolve(by=['cod_prov','nomvia','grupo'])
        ultima_union['geom'] = ultima_union['geom'].apply(lambda geom: linemerge(geom) if geom.geom_type == 'MultiLineString' else geom)
        #--
        marcas=[]
        #Buscar cada registro de puntos_agrupados
        for row1 in puntos_agrupados.itertuples(index=False):
            puntos = gpd.GeoSeries(row1[3])
            busqueda = ultima_union[(ultima_union.index.get_level_values(0) == row1[0]) &
                        (ultima_union.index.get_level_values(1) == row1[1]) &
                        (ultima_union.index.get_level_values(2) != row1[2])]
            #Buscar mismo distrito y nombre pero otro grupo, para encontrar el punto mas cercano del grupo original a los otros grupos
            for row2 in busqueda.itertuples(index=False): 
                linea = row2[0]
                distancias = puntos.distance(linea)
                indice_punto_cercano = distancias.idxmin()
                punto_mas_cercano = puntos[indice_punto_cercano]
                marcas.append((row1[0],row1[1],punto_mas_cercano))
        #--
        gdf = gpd.GeoDataFrame(marcas, columns=['cod_prov', 'nomvia', 'geom'], geometry='geom')        
        gdf.set_crs("EPSG:4326", allow_override=True, inplace=True)
        #-
        result = gpd.sjoin(filtro, gdf, how="left", predicate='intersects')
        result = result[(result['cod_prov_left'] == result['cod_prov_right']) & (result['nomvia_left'] == result['nomvia_right'])].copy()

        #mini joined
        def get_start_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, simplemente tomamos el primer punto
                return Point(geom.coords[0])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el primer punto del primer LineString
                first_line = list(geom.geoms)[0]
                return Point(first_line.coords[0])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None

        # Función para obtener el punto final de una geometría, sea LineString o MultiLineString
        def get_end_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, tomamos el último punto
                return Point(geom.coords[-1])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el último punto del último LineString
                last_line = list(geom.geoms)[-1]
                return Point(last_line.coords[-1])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None
        # Definir función para calcular el azimuth entre dos puntos
        def calculate_azimuth(start, end):
            dx = end.x - start.x
            dy = end.y - start.y

            angle_rad = atan2(dx, dy)
            angle_deg = degrees(angle_rad)

            # Normalizar a rango 0–360
            if angle_deg < 0:
                angle_deg += 360
            
            return angle_deg

        # Clasificar las relaciones en 'Paralelas', 'Perpendiculares', o 'No son paralelas ni perpendiculares'
        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < 30:
                return 'Paralelas'
            elif 30 < diferencia_orientacion < 150:
                return 'Perpendiculares'
            elif  150< diferencia_orientacion < 210:
                return 'Paralelas invertidas'
            elif  210< diferencia_orientacion < 360:
                return 'Perpendiculares'
            else:
                return 'No son paralelas ni perpendiculares'
                
        filtro['punto_inicio'] = filtro['geom'].apply(get_start_point)
        filtro['punto_fin'] = filtro['geom'].apply(get_end_point)
        filtro['orientacion'] = filtro.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        filtroindices=filtro.loc[list(result.index.unique())]
        joined = gpd.sjoin(filtroindices, filtro, how='left', predicate='intersects', lsuffix='1', rsuffix='2')
        joined = joined[joined['id_1']!=joined['id_2']]

        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        joined['relacion'] = joined['diferencia_orientacion'].apply(clasificar_relacion)
        paralelas_continuidad = joined[(joined['relacion'] == 'Paralelas') | (joined['relacion'] == 'Paralelas invertidas')].copy()

        Marcafinal = set(paralelas_continuidad[(paralelas_continuidad['cod_prov_1']==paralelas_continuidad['cod_prov_2']) & (paralelas_continuidad['nomvia_1']!=paralelas_continuidad['nomvia_2'])][['id_1','cod_prov_1','nomvia_1','id_2','cod_prov_2','nomvia_2']].index)

        cond1 = mv_chile.index.isin(Marcafinal)
        cond2 = mv_chile['incidencia'].isna()
        cond3 = mv_chile['exclusion'].str.contains(r'\[7\]', na=False)
        mv_chile.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_chile['incidencia'] + " - 6. Revisar Continuidad"
        mv_chile.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "6. Revisar Continuidad"

    if key == 7: 
        #7 salto generadora
        filtro = mv_chile[(mv_chile['cod_prov']==texto_filtro) & (~mv_chile['nomvtotal'].str.contains('S/N', na=False))].copy()

        # Función para obtener el punto inicial de una geometría, sea LineString o MultiLineString
        def get_start_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, simplemente tomamos el primer punto
                return Point(geom.coords[0])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el primer punto del primer LineString
                first_line = list(geom.geoms)[0]
                return Point(first_line.coords[0])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None

        # Función para obtener el punto final de una geometría, sea LineString o MultiLineString
        def get_end_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, tomamos el último punto
                return Point(geom.coords[-1])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el último punto del último LineString
                last_line = list(geom.geoms)[-1]
                return Point(last_line.coords[-1])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None

        # Definir función para calcular el azimuth entre dos puntos
        def calculate_azimuth(start, end):
            dx = end.x - start.x
            dy = end.y - start.y

            angle_rad = atan2(dx, dy)
            angle_deg = degrees(angle_rad)

            # Normalizar a rango 0–360
            if angle_deg < 0:
                angle_deg += 360
            
            return angle_deg

        # Aplicar función a cada geometría (asumiendo que son LineStrings)
        filtro['punto_inicio'] = filtro['geom'].apply(get_start_point)
        filtro['punto_fin'] = filtro['geom'].apply(get_end_point)
        filtro['orientacion'] = filtro.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        #Agregarlongitud
        filtro['longitud'] = filtro.to_crs(epsg=3857).geometry.length
        #-----------------------------------------

        # Unir el GeoDataFrame consigo mismo para comparar segmentos cercanos o que se intersectan
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
        # Filtrar donde no sean la misma línea
        joined = joined[joined['id_1'] != joined['id_2']]

        # Calcular diferencias de orientación
        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        # Clasificar las relaciones en 'Paralelas', 'Perpendiculares', o 'No son paralelas ni perpendiculares'
        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < 30:
                return 'Paralelas'
            elif 30 < diferencia_orientacion < 150:
                return 'Perpendiculares'
            elif  150< diferencia_orientacion < 210:
                return 'Paralelas invertidas'
            elif  210< diferencia_orientacion < 360:
                return 'Perpendiculares'
            else:
                return 'No son paralelas ni perpendiculares'

        joined['relacion'] = joined['diferencia_orientacion'].apply(clasificar_relacion)
        joined['generadora_1'] = pd.to_numeric(joined['generadora_1'])
        joined['generadora_2'] = pd.to_numeric(joined['generadora_2'])

        #Necesarioparalo nuevo
        joined.loc[(joined['punto_inicio_1'].intersects(joined['punto_inicio_2'])|(joined['punto_inicio_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'inicio'
        joined.loc[(joined['punto_fin_1'].intersects(joined['punto_inicio_2'])|(joined['punto_fin_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'fin'
        counts = joined.groupby('id_1').agg(
            total=('id_1', 'size'),
            inicio_count=('conexion', lambda x: (x.str.contains('inicio')).sum()),
            final_count=('conexion', lambda x: (x.str.contains('fin')).sum())
        ).reset_index()
        joined.reset_index(drop=False,inplace=True)
        joined = joined.merge(counts[['id_1', 'inicio_count','final_count']], on='id_1', how='left')
        joined.loc[joined['conexion']=='fin','validacion_t']=joined['final_count']
        joined.loc[joined['conexion']=='inicio','validacion_t']=joined['inicio_count']
        #------------------------------------
        joined.set_index('index', inplace=True)
        joined_generadoras = joined.dropna(subset=['generadora_1','generadora_2'])
        paralelas_generadoras = joined_generadoras[(joined_generadoras['relacion'] == 'Paralelas') | (joined_generadoras['relacion'] == 'Paralelas invertidas')]
        paralelas_generadoras_via = paralelas_generadoras[paralelas_generadoras['nomvtotal_1'] == paralelas_generadoras['nomvtotal_2']].copy()
        paralelas_generadoras_via['resta']=paralelas_generadoras_via['generadora_2']-paralelas_generadoras_via['generadora_1']

        #quitar Ts y lineas menores a 15 metros 
        paralelas_generadoras_via=paralelas_generadoras_via[~((paralelas_generadoras_via['resta']==0) & (paralelas_generadoras_via['validacion_t']==2))]
        paralelas_generadoras_via = paralelas_generadoras_via[~(((paralelas_generadoras_via['longitud_1'] < 15) | (paralelas_generadoras_via['longitud_2'] < 15)) & (paralelas_generadoras_via['resta'] == 0))]
        #------------------------

        saltos_gen=paralelas_generadoras_via[(paralelas_generadoras_via['resta' ]!=1) & (paralelas_generadoras_via['resta' ]!=-1)].index

        #MARCAR 
        cond1 = mv_chile.index.isin(saltos_gen)
        cond2 = mv_chile['incidencia'].isna()
        cond3 = mv_chile['exclusion'].str.contains(r'\[7\]', na=False)
        mv_chile.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_chile['incidencia'] + " - 7. Salto generadora"
        mv_chile.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "7. Salto generadora"

    if key == 8:
            
        #8 Error apuntamiento
        filtro = mv_chile[(mv_chile['cod_prov']==texto_filtro)].copy()

        # Función para obtener el punto inicial de una geometría, sea LineString o MultiLineString
        def get_start_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, simplemente tomamos el primer punto
                return Point(geom.coords[0])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el primer punto del primer LineString
                first_line = list(geom.geoms)[0]
                return Point(first_line.coords[0])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None

        # Función para obtener el punto final de una geometría, sea LineString o MultiLineString
        def get_end_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, tomamos el último punto
                return Point(geom.coords[-1])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el último punto del último LineString
                last_line = list(geom.geoms)[-1]
                return Point(last_line.coords[-1])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None

        # Definir función para calcular el azimuth entre dos puntos
        def calculate_azimuth(start, end):
            dx = end.x - start.x
            dy = end.y - start.y

            angle_rad = atan2(dx, dy)
            angle_deg = degrees(angle_rad)

            # Normalizar a rango 0–360
            if angle_deg < 0:
                angle_deg += 360
            
            return angle_deg

        # Aplicar función a cada geometría (asumiendo que son LineStrings)
        filtro['punto_inicio'] = filtro['geom'].apply(get_start_point)
        filtro['punto_fin'] = filtro['geom'].apply(get_end_point)
        filtro['orientacion'] = filtro.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        # Unir el GeoDataFrame consigo mismo para comparar segmentos cercanos o que se intersectan
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
        # Filtrar donde no sean la misma línea
        joined = joined[joined['id_1'] != joined['id_2']]

        # Calcular diferencias de orientación
        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        # Clasificar las relaciones en 'Paralelas', 'Perpendiculares', o 'No son paralelas ni perpendiculares'
        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < 30:
                return 'Paralelas'
            elif 30 < diferencia_orientacion < 150:
                return 'Perpendiculares'
            elif  150< diferencia_orientacion < 210:
                return 'Paralelas invertidas'
            elif  210< diferencia_orientacion < 360:
                return 'Perpendiculares'
            else:
                return 'No son paralelas ni perpendiculares'

        joined['relacion'] = joined['diferencia_orientacion'].apply(clasificar_relacion)
        # Filtrar por relaciones 'Paralelas'
        paralelas = joined[(joined['relacion'] == 'Paralelas') | (joined['relacion'] == 'Paralelas invertidas')].copy()
        
        paralelas_apuntamiento = paralelas[paralelas['relacion'] == 'Paralelas invertidas'].copy()
        paralelas_apuntamiento['cruce_final'] = paralelas_apuntamiento.apply(
            lambda row: row['punto_fin_1'].intersects(row['punto_fin_2']),
            axis=1
        )
        paralelas_apuntamiento.index = pd.MultiIndex.from_arrays([paralelas_apuntamiento.index, paralelas_apuntamiento['index_2']])
        Errores=paralelas_apuntamiento[paralelas_apuntamiento['cruce_final']==True]
        errores_apuntamiento=set(Errores.index.get_level_values(0).unique())|set(Errores.index.get_level_values(1).unique())
        cond1 = mv_chile.index.isin(errores_apuntamiento)
        cond2 = mv_chile['incidencia'].isna()
        cond3 = mv_chile['exclusion'].str.contains(r'\[8\]', na=False)
        mv_chile.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_chile['incidencia'] + " - 8. Error apuntamiento"
        mv_chile.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "8. Error apuntamiento"

    # 9-10-11 Orientacion Frente a Par e Impar
    if key == 9 :
    
        def get_start_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, simplemente tomamos el primer punto
                return Point(geom.coords[0])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el primer punto del primer LineString
                first_line = list(geom.geoms)[0]
                return Point(first_line.coords[0])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None
        def get_end_point(geom):
            if isinstance(geom, LineString):
                # Si es un LineString, tomamos el último punto
                return Point(geom.coords[-1])
            elif isinstance(geom, MultiLineString):
                # Si es un MultiLineString, tomamos el último punto del último LineString
                last_line = list(geom.geoms)[-1]
                return Point(last_line.coords[-1])
            else:
                # Si no es ni LineString ni MultiLineString, retornamos None
                return None

        # Definir función para calcular el azimuth entre dos puntos
        def calcular_azimuth(start, end):
            dx = end.x - start.x
            dy = end.y - start.y
            return atan2(dy, dx)

        def min_max_placa(group,include_groups=False):
            min_placa = group.loc[group['placa'].idxmin()]
            max_placa = group.loc[group['placa'].idxmax()]
            return pd.Series({
                'min_placa': min_placa['placa'],
                'ind_pl_min': min_placa['ind_pl'],
                'max_placa': max_placa['placa'],
                'ind_pl_max': max_placa['ind_pl']
            })

        filtro = placas_chile[(placas_chile['cod_prov']==texto_filtro)].dropna(subset=['nomvtotal','generadora'])
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=2))
            resultados.append([row.Index,candidates[0],candidates[1]])
        copia_malla = mv_chile.copy()
        copia_malla['list_generadora']=copia_malla['generadora'].apply(lambda x: [''] if x is None else x.split('|'))
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno','mv_dos'])
        combo=[]
        for row in resultados_df.itertuples(index=False):
            if ((placas_chile.at[row[0], 'nomvtotal']==copia_malla.at[row[1], 'nomvtotal']) and (placas_chile.at[row[0], 'generadora'] in copia_malla.at[row[1], 'list_generadora'])):
                combo.append([row[1],row[0],placas_chile.at[row[0],'placa']])
            elif ((placas_chile.at[row[0], 'nomvtotal']==copia_malla.at[row[2], 'nomvtotal']) and (placas_chile.at[row[0], 'generadora'] in copia_malla.at[row[2], 'list_generadora'])):
                combo.append([row[2],row[0],placas_chile.at[row[0],'placa']])
        combo_df = pd.DataFrame(combo,columns=['ind_mv','ind_pl','placa'])
        combo_df['placa']= pd.to_numeric(combo_df['placa'])
        impar= combo_df[(combo_df['placa'] % 2 == 1)]
        par= combo_df[(combo_df['placa'] % 2 == 0)]

        list_par_uno = par['ind_mv'].value_counts()[par['ind_mv'].value_counts() == 1].index.tolist()
        list_impar_uno = impar['ind_mv'].value_counts()[impar['ind_mv'].value_counts() == 1].index.tolist()

        par = par[~par['ind_mv'].isin(list_par_uno)]
        impar = impar[~impar['ind_mv'].isin(list_impar_uno)]

        par_fin = par.groupby('ind_mv').apply(min_max_placa, include_groups=False).reset_index()
        impar_fin  = impar.groupby('ind_mv').apply(min_max_placa, include_groups=False).reset_index()

        mala_orientacion = set()
        for row in impar_fin.itertuples(index = False):
            az_mv = calcular_azimuth(get_start_point(mv_chile.loc[row[0],'geom']),get_end_point(mv_chile.loc[row[0],'geom']))
            az_mv = radians((degrees(az_mv)+360)%360)
            az_p = calcular_azimuth(placas_chile.loc[row[2],'geom'],placas_chile.loc[row[4],'geom'])
            az_p = radians((degrees(az_p)+360)%360)
            if abs(az_mv-az_p)>radians(100):
                mala_orientacion.add(row[0])
        par_fin=par_fin[~par_fin['ind_mv'].isin(mala_orientacion)]
        for row in par_fin.itertuples(index = False):
            az_mv = calcular_azimuth(get_start_point(mv_chile.loc[row[0],'geom']),get_end_point(mv_chile.loc[row[0],'geom']))
            az_mv = radians((degrees(az_mv)+360)%360)
            az_p = calcular_azimuth(placas_chile.loc[row[2],'geom'],placas_chile.loc[row[4],'geom'])
            az_p = radians((degrees(az_p)+360)%360)
            if abs(az_mv-az_p)>radians(100):
                mala_orientacion.add(row[0])
        #MARCAR 
        cond1 = mv_chile.index.isin(mala_orientacion)
        cond2 = mv_chile['incidencia'].isna()
        cond3 = mv_chile['exclusion'].str.contains(r'\[9\]', na=False)
        mv_chile.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_chile['incidencia'] + " - 9. Invertir vector"
        mv_chile.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "9. Invertir vector"

        
    if key ==10 :
        #10 RANGO

        agrupados = mv_chile[(mv_chile['cod_prov']==texto_filtro) & (~mv_chile['nomvia'].str.contains('S/N', na=False))][['cod_prov','tipovia','nomvia','generadora']].dropna().drop_duplicates()
        copia_placas = placas_chile[(placas_chile['cod_prov']==texto_filtro) & (~placas_chile['nomvia'].str.contains('S/N', na=False)) & (placas_chile['atipico'].isna())][['cod_prov','tipovia','nomvia','generadora','placa']].dropna().set_index(['cod_prov','tipovia','nomvia','generadora']).sort_index()
        sin_ran = set()
        sin_par = set()
        sin_impar = set()
        for row in agrupados.itertuples():
            try:
                filtro = copia_placas.loc[(row[1],row[2],row[3],row[4])].sort_values(by='placa').set_index('placa')
            except Exception as e:
                sin_ran.add(row[0])
                continue
            indices = filtro.index.tolist()
            pares = [int(re.sub(r'\D', '', num)) for num in indices if int(re.sub(r'\D', '', num)) % 2 == 0]
            impares = [int(re.sub(r'\D', '', num)) for num in indices if int(re.sub(r'\D', '', num)) % 2 != 0]
            if len(pares)>0:
                mv_chile.at[row[0],'rangopar']=f"{pares[0]}, {pares[-1]}"
            else:
                sin_par.add(row[0])
            if len(impares)>0:
                mv_chile.at[row[0],'rangoimpar']=f"{impares[0]},{impares[-1]}"
            else:
                sin_impar.add(row[0])
        #MARCAR 
        cond1 = mv_chile.index.isin(sin_ran|sin_par)
        mv_chile.loc[cond1 , 'rangopar'] = "Sin rango par"

        #MARCAR 
        cond1 = mv_chile.index.isin(sin_ran|sin_impar)
        mv_chile.loc[cond1 , 'rangoimpar'] = "Sin rango impar"
    
    return mv_chile
    
def Chile_validar_mv(engine, mavvial, placas, texto_filtro, seleccionados):
    
    campos_1 = 'id,geom,nom_reg,nom_prov,tipovia,nomvia,nomvtotal,atipico'
    campos_2 = 'id,geom,id_capa,atipico'
    campos_3 = 'id,geom,cod_reg,cod_prov,nomvia,generadora,atipico'
    campos_4 = 'id,geom,cod_reg,cod_prov,generadora,atipico'
    campos_5 = 'id,geom,cod_reg,cod_prov,cod_com,nomvtotal,generadora,costado,atipico'  
    campos_6 = 'id,geom,cod_reg,cod_prov,nomvtotal,atipico'
    campos_7 = 'id,geom,cod_reg,cod_prov,nomvtotal,generadora,atipico'   
    campos_8 = 'id,geom,cod_reg,cod_prov,nomvtotal,generadora,atipico'
    campos_9 = 'id,geom,cod_reg,cod_prov,tipovia,nomvia,nomvtotal,generadora,atipico'
    campos_10 = 'id,geom,cod_reg,cod_prov,tipovia,nomvia,generadora,atipico'
    
    campos = {1:campos_1,2:campos_2,3:campos_3,4:campos_4,5:campos_5,6:campos_6,7:campos_7,8:campos_8,9:campos_9,10:campos_10}

    # Crear un conjunto para almacenar campos únicos
    columnas_consulta = set()

    # Recorrer los campos seleccionados y agregar los valores al conjunto
    for key in seleccionados:
        if key in campos:
            columnas_consulta.update(campos[key].split(','))  # Dividir por coma y agregar cada campo al conjunto

    # Convertir los campos únicos a una cadena concatenada
    final_fields = ", ".join(sorted(columnas_consulta))  # Ordenar para mayor legibilidad
    #print(final_fields)
    
    # ********* Como Traer la Mavvial al DataFrame *********

    sql = f"SELECT {final_fields} FROM {mavvial} WHERE cod_prov = '{texto_filtro}';"
    mv_chile = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
    mv_chile['incidencia'] = None   
    mv_chile['rangopar'] = None  
    mv_chile['rangoimpar'] = None  
    mv_chile['exclusion'] = mv_chile['atipico'].apply(
        lambda mi_string: ','.join([f"[{x}]" for x in mi_string.replace(" ", "").split(",")]) 
        if mi_string is not None else None
	)
                                  
            
    if (set(seleccionados) - {1,2,3,4,5,6,7,8}) != set():#Que no
        sql=f"SELECT id,geom,cod_reg,cod_prov,tipovia,nomvia,nomvtotal,generadora,placa,atipico FROM {placas} WHERE cod_prov = '{texto_filtro}';"
        placas_chile = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
    
        if ({9} & set(seleccionados)) != set():#Que si
            idx = indexx.Index()
            #Agregar líneas al índice
            for i, geometry in enumerate(mv_chile.geometry):
                if geometry is not None:
                    idx.insert(i, geometry.bounds)
        else:
            idx=''
    else:
        placas_chile=''
        idx=''
    
    for key in seleccionados:
        mv_chile = Chile_mv_incidencia( mv_chile, placas_chile, texto_filtro, key,idx)
    
    df_temporal = mv_chile[['id', 'incidencia', 'rangopar', 'rangoimpar']]
    df_temporal.to_sql('tabla_temporal', con=engine, index=False, if_exists='replace')