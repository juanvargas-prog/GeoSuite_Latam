def Brasil_QueryValMavvial(mavvial,placas):
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
          
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX REEMPLAZAR SIMBOLOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/  
    UPDATE """ + mavvial + """ SET nom_estado = regexp_replace(nom_estado, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_estado ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + mavvial + """ SET nom_mun = regexp_replace(nom_mun, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_mun ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';

    UPDATE """ + mavvial + """ SET nom_distri = regexp_replace(nom_distri, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_distri ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + mavvial + """ SET nomvia = regexp_replace(nomvia, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nomvia ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]'
    AND nomvia != 'S/N';

    UPDATE """ + mavvial + """ SET nomvtotal = regexp_replace(nomvtotal, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nomvtotal ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]'
    AND nomvtotal != 'S/N';
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX PASAR A MAYUSCULAS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_estado = UPPER(nom_estado) WHERE nom_estado <> UPPER(nom_estado);
    UPDATE """ + mavvial + """ SET nom_mun = UPPER(nom_mun) WHERE nom_mun <> UPPER(nom_mun);
    UPDATE """ + mavvial + """ SET nom_distri = UPPER(nom_distri) WHERE nom_distri <> UPPER(nom_distri);
    UPDATE """ + mavvial + """ SET nomvia = UPPER(nomvia) WHERE nomvia <> UPPER(nomvia);
    UPDATE """ + mavvial + """ SET nomvtotal = UPPER(nomvtotal) WHERE nomvtotal <> UPPER(nomvtotal);
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR ESPACIOS INICIO-FIN XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_estado = TRIM(nom_estado) WHERE nom_estado <> TRIM(nom_estado);
    UPDATE """ + mavvial + """ SET nom_mun = TRIM(nom_mun) WHERE nom_mun <> TRIM(nom_mun);
    UPDATE """ + mavvial + """ SET nom_distri = TRIM(nom_distri) WHERE nom_distri <> TRIM(nom_distri);
    UPDATE """ + mavvial + """ SET nomvia = TRIM(nomvia) WHERE nomvia <> TRIM(nomvia);
    UPDATE """ + mavvial + """ SET nomvtotal = TRIM(nomvtotal) WHERE nomvtotal <> TRIM(nomvtotal);

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR DOBLES ESPACIOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_estado = REPLACE(nom_estado,'  ',' ') WHERE nom_estado LIKE '%  %';
    UPDATE """ + mavvial + """ SET nom_mun = REPLACE(nom_mun,'  ',' ') WHERE nom_mun LIKE '%  %';
    UPDATE """ + mavvial + """ SET nom_distri = REPLACE(nom_distri,'  ',' ') WHERE nom_distri LIKE '%  %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'  ',' ') WHERE nomvia LIKE '%  %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'  ',' ') WHERE nomvtotal LIKE '%  %';   
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX TODOS LOS NUMEROS VAN SEPARADOS DE LAS LETRASXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nomvia = regexp_replace(nomvia,'([A-Za-z])([0-9])','\\1 \\2','g')
    WHERE nomvia ~ '([A-Za-z][0-9])';

    UPDATE """ + mavvial + """ SET nomvia = regexp_replace(nomvia,'([0-9])([A-Za-z])','\\1 \\2','g')
    WHERE nomvia ~ '([0-9][A-Za-z])';

    UPDATE """ + mavvial + """ SET nomvtotal = regexp_replace(nomvtotal,'([A-Za-z])([0-9])','\\1 \\2','g')
    WHERE nomvtotal ~ '([A-Za-z][0-9])';

    UPDATE """ + mavvial + """ SET nomvtotal = regexp_replace(nomvtotal,'([0-9])([A-Za-z])','\\1 \\2','g')
    WHERE nomvtotal ~ '([0-9][A-Za-z])';

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXNUMERO ESPACIO LETRA ESPACIO LETRA SE DEBEN UNIRXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    
    UPDATE """ + mavvial + """ SET nomvia = regexp_replace(nomvia,'([0-9]) ([A-Za-z]) ([A-Za-z])\\b','\\1 \\2\\3','g')
    WHERE nomvia ~ '([0-9]) ([A-Za-z]) ([A-Za-z])\\b';    
    
    UPDATE """ + mavvial + """ SET nomvtotal = regexp_replace(nomvtotal,'([0-9]) ([A-Za-z]) ([A-Za-z])\\b','\\1 \\2\\3','g')
    WHERE nomvtotal ~ '([0-9]) ([A-Za-z]) ([A-Za-z])\\b'; 
    
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

def Brasil_mv_incidencia(mv_brasil, placas_brasil, texto_filtro, key,idx):

    mifiltro=texto_filtro #####AQUI VA EL FILTRO#####
    partes = mifiltro.split(',')
    dep=partes[0]
    prov=partes[1]
            
    if key ==1 :

        # 1. Validar registro con caracteres
        id_excp = list(mv_brasil.loc[mv_brasil['exclusion'].str.contains(r'\[1\]', na=False),'id'])
        # Expresión regular para caracteres especiales
        simbolos = r'[|!"#@$%&/()¿¡¨{}\[\]._:,;+\-*=/¬°]'

        # Función para marcar la inconsistencia si hay caracteres especiales en alguna columna específica
        def marcar_simbolos(row):
            if row['nomvia'] != 'S/N':
                columnas = ['nom_estado', 'nom_mun', 'nom_distri', 'tipovia', 'nomvia', 'nomvtotal']
                for col in columnas:
                    if pd.notna(row[col]) and re.search(simbolos, row[col]) and (row['id'] not in id_excp):
                        return '1. Validar registro con caracteres - '
            return None

        # Aplicar la función para marcar incidencia
        mv_brasil['incidencia'] = mv_brasil.apply(marcar_simbolos, axis=1)
        
    if key == 2:
    
        #2 id_capa duplicado
        frecuencias = mv_brasil['id_capa'].value_counts().reset_index()
        valor_dict = frecuencias[frecuencias['count'] > 1].set_index('id_capa')['count'].to_dict()
        id_excp = list(mv_brasil.loc[mv_brasil['exclusion'].str.contains(r'\[2\]', na=False),'id'])
        mv_brasil['incidencia'] = mv_brasil.apply(
            lambda row: f"{row['incidencia']} - 2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is not None and row['id_capa'] in valor_dict and row['id'] not in id_excp  else 
            f"2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is  None and row['id_capa'] in valor_dict and row['id'] not in id_excp  else
            row['incidencia'],
            axis=1
        )

    if key == 3:        
        #3 Campo nomvia es vacio
        filtro = mv_brasil[(mv_brasil['cod_estado']==dep) & (mv_brasil['cod_mun']==prov)].copy()

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
            return atan2(dy, dx)

        # Aplicar función a cada geometría (asumiendo que son LineStrings)
        filtro['punto_inicio'] = filtro['geom'].apply(get_start_point)
        filtro['punto_fin'] = filtro['geom'].apply(get_end_point)
        filtro['orientacion'] = filtro.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        #Agregarlongitud
        filtro['longitud'] = filtro.to_crs(epsg=3857).geometry.length
        #-----------------------------------------

        # Unir el GeoDataFrame consigo mismo para comparar segmentos cercanos o que se intersectan
        joined = gpd.sjoin(filtro, filtro, how='inner', op='intersects', lsuffix='1', rsuffix='2')
        # Filtrar donde no sean la misma línea
        joined = joined[joined['id_1'] != joined['id_2']]

        # Calcular diferencias de orientación
        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        # Clasificar las relaciones en 'Paralelas', 'Perpendiculares', o 'No son paralelas ni perpendiculares'
        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < radians(30):
                return 'Paralelas'
            elif radians(70) < diferencia_orientacion < radians(110):
                return 'Perpendiculares'
            elif radians(150) < diferencia_orientacion < radians(210):#----------------#
                return 'Paralelas invertidas'
            else:
                return 'No son paralelas ni perpendiculares'

        joined['relacion'] = joined['diferencia_orientacion'].apply(clasificar_relacion)
        saltos_cuadras=[]

        paralelas_nombres = joined[(joined['relacion'] == 'Paralelas') | (joined['relacion'] == 'Paralelas invertidas')]
        SN=paralelas_nombres[((paralelas_nombres['nomvia_1'].isna()) | (paralelas_nombres['nomvia_1'].str.contains('S/N',na=False))) & (paralelas_nombres['longitud_1'] > 15)]
        idnulo = SN[(SN['nomvia_2'].notna()) & ~(SN['nomvia_2'].str.contains('S/N',na=False))].index.unique()

        cond1 = mv_brasil.index.isin(idnulo)
        cond2 = mv_brasil['incidencia'].isna()
        cond3 = mv_brasil['exclusion'].str.contains(r'\[3\]', na=False)
        mv_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_brasil['incidencia'] + " - 3. nomvia vacio"
        mv_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "3. nomvia vacio"
        
    if key == 4:    

        # 4 generadora (generadora) es vacio
        filtro = mv_brasil[(mv_brasil['cod_estado']==dep) & (mv_brasil['cod_mun']==prov)].copy()

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
            return atan2(dy, dx)

        # Aplicar función a cada geometría (asumiendo que son LineStrings)
        filtro['punto_inicio'] = filtro['geom'].apply(get_start_point)
        filtro['punto_fin'] = filtro['geom'].apply(get_end_point)
        filtro['orientacion'] = filtro.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        #Agregarlongitud
        filtro['longitud'] = filtro.to_crs(epsg=3857).geometry.length
        #-----------------------------------------
        filtro['list_generadora']=filtro['generadora'].apply(lambda x: [''] if x is None else x.split('|'))
        # Unir el GeoDataFrame consigo mismo para comparar segmentos cercanos o que se intersectan
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
        # Filtrar donde no sean la misma línea
        joined = joined[joined['id_1'] != joined['id_2']]
        #Hallar tipo de conexion
        joined.loc[(joined['punto_inicio_1'].intersects(joined['punto_inicio_2'])|(joined['punto_inicio_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'inicio'
        joined.loc[(joined['punto_fin_1'].intersects(joined['punto_inicio_2'])|(joined['punto_fin_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'fin'
        # Calcular diferencias de orientación
        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        # Clasificar las relaciones en 'Paralelas', 'Perpendiculares', o 'No son paralelas ni perpendiculares'
        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < radians(30):
                return 'Paralelas'
            elif radians(70) < diferencia_orientacion < radians(110):
                return 'Perpendiculares'
            elif radians(150) < diferencia_orientacion < radians(210):#----------------#
                return 'Paralelas invertidas'
            else:
                return 'No son paralelas ni perpendiculares'

        joined['relacion'] = joined['diferencia_orientacion'].apply(clasificar_relacion)

        #GEN1 NULO PER GEN2 NO
        paralelas_generadora = joined[(joined['relacion'] == 'Paralelas') | (joined['relacion'] == 'Paralelas invertidas')]
        SG1=paralelas_generadora[(paralelas_generadora['generadora_1'].isna()) & (paralelas_generadora['longitud_1']>15) ]
        SG2=SG1[(SG1['generadora_2'].notna())]
        #--
        #SOLO TOCA CON UNO Y GEN 2 NO ES 0
        repeated_indices = SG2.index.value_counts()
        repeated_indices_uno = repeated_indices[repeated_indices == 1].index
        SG3=SG2.loc[repeated_indices_uno]
        ind_gen_vacio_p1=set(SG3[~SG3['list_generadora_2'].apply(lambda x: '0' in x)].index) #SI MARCA
        #--
        #SOLO TOCA CON UNO Y ES MISMO DISTRITO Y MISMO NOMVTOTAL Y GEN 2 NO ES 0
        SG4 = SG2.loc[~SG2.index.isin(repeated_indices_uno)]
        SG5 = SG4[(SG4['cod_distri_1']==SG4['cod_distri_2']) & (SG4['nomvtotal_1']==SG4['nomvtotal_2'])]
        repeated_indices = SG5.index.value_counts()
        repeated_indices_uno = repeated_indices[repeated_indices == 1].index
        SG6 = SG5.loc[repeated_indices_uno]
        ind_gen_vacio_p2=set(SG6[~SG6['list_generadora_2'].apply(lambda x: '0' in x)].index) #SI MARCA
        #--
        #QUITAR LOS QUE TOCAN CON 3. SE EVALUO Y SE PUDEN QUITAR TODOS
        SG7 = SG5.loc[~SG5.index.isin(repeated_indices_uno)]
        repeated_indices = SG7.index.value_counts()
        repeated_indices_tres = repeated_indices[repeated_indices > 2].index
        SG8=SG7.loc[~SG7.index.isin(repeated_indices_tres)]
        #--
        #MULTIPLE INICIO O DOBLE FINAL QUE ALGUNO TIENE UN 0 EN GENERADORA
        conteo_conexiones = SG8.reset_index(drop=False).groupby(['index', 'conexion']).size().unstack(fill_value=0)
        tocandocero=SG8[SG8.index.isin(conteo_conexiones[(conteo_conexiones['fin']==0) | (conteo_conexiones['inicio']==0)].index) & (SG8['list_generadora_2'].apply(lambda x: '0' in x))].index
        ind_gen_vacio_p3=set(list(conteo_conexiones[conteo_conexiones['fin']!=1].index))-set(tocandocero) #SI MARCA
        SG9 = SG8[~SG8.index.isin(conteo_conexiones[conteo_conexiones['fin']!=1].index)]
        #--
        #VALIDACION SALTO
        SG9inicio = SG9.loc[SG9['conexion']=='inicio'].copy()
        SG9fin = SG9.loc[SG9['conexion']=='fin'].copy()
        SG9inicio['valor_comp']= SG9inicio['list_generadora_2'].apply(lambda x: max(list(map(int, x))) )
        SG9fin['valor_comp']= SG9fin['list_generadora_2'].apply(lambda x: min(list(map(int, x))) )
        SG10 = pd.merge(SG9inicio.reset_index(drop=False)[['index', 'valor_comp']], SG9fin.reset_index(drop=False)[['index', 'valor_comp']], on='index', how='inner', suffixes=('_1', '_2'))
        SG10['resta']=SG10['valor_comp_2']-SG10['valor_comp_1']
        ind_gen_vacio_p4=set(SG10[~(SG10['resta']==0) & ~(SG10['resta']==100)]['index']) #SI MARCA
        #--

        generadoranulo = ind_gen_vacio_p1 | ind_gen_vacio_p2 | ind_gen_vacio_p3 | ind_gen_vacio_p4

        cond1 = mv_brasil.index.isin(generadoranulo)
        cond2 = mv_brasil['incidencia'].isna()
        cond3 = mv_brasil['exclusion'].str.contains(r'\[4\]', na=False)
        mv_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_brasil['incidencia'] + " - 4. Generadora vacia"
        mv_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "4. Generadora vacia" 
        
    if key == 5:     
        #5 CRUCE REPETIDO
        #P1
        copia_malla=mv_brasil[(mv_brasil['cod_estado']==dep) & (mv_brasil['cod_mun']==prov) &(~mv_brasil['nomvtotal'].str.contains('S/N', na=False))].dropna(subset=['cod_estado', 'cod_mun','cod_distri','nomvtotal','generadora'])
        copia_malla['longitud'] = copia_malla.to_crs(epsg=3857).geometry.length
        mallamas15=copia_malla[copia_malla['longitud']>15]
        def duplicar_por_valores_1(df, columna):
            registros_duplicados = []
            for row in df.itertuples():
                valores = row._asdict()[columna].split('|')
                valores_unicos = sorted(valores)
                for valor in valores_unicos:
                    registro_duplicado = row._asdict()
                    registro_duplicado[columna] = valor
                    registros_duplicados.append(registro_duplicado)
            return gpd.GeoDataFrame(registros_duplicados,geometry='geom')
        copia_malla=copia_malla.reset_index(drop=False).set_index(['cod_estado','cod_mun','cod_distri','nomvtotal','generadora']).sort_index()
        mallamas15 = duplicar_por_valores_1(mallamas15, 'generadora')

        mallamas15 = mallamas15.set_index(['cod_estado','cod_mun','cod_distri','nomvtotal','generadora']).sort_index()
        repeated_indices = mallamas15.index.value_counts()
        repeated_indices = repeated_indices[repeated_indices > 1].index
        ind_rep_p1 = set(mallamas15.loc[repeated_indices,'Index'])

        #P2
        prep2=mallamas15.loc[repeated_indices].reset_index(drop=False).set_index('Index')

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
            return atan2(dy, dx)

        # Aplicar función a cada geometría (asumiendo que son LineStrings)
        prep2['punto_inicio'] = prep2['geom'].apply(get_start_point)
        prep2['punto_fin'] = prep2['geom'].apply(get_end_point)
        prep2['orientacion'] = prep2.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        joined = gpd.sjoin(prep2[['id','geom','cod_distri','nomvtotal','generadora','orientacion']], prep2[['id','geom','cod_distri','nomvtotal','generadora','orientacion']], how='inner', predicate='intersects', lsuffix='1', rsuffix='2')

        joined = joined[joined['id_1'] != joined['id_2']]
        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < radians(30):
                return 'Paralelas'
            elif radians(70) < diferencia_orientacion < radians(110):
                return 'Perpendiculares'
            elif radians(150) < diferencia_orientacion < radians(210):#----------------#
                return 'Paralelas invertidas'
            else:
                return 'No son paralelas ni perpendiculares'

        joined['relacion'] = joined['diferencia_orientacion'].apply(clasificar_relacion)
        paralelas_repetidas = joined[(joined['relacion'] == 'Paralelas') | (joined['relacion'] == 'Paralelas invertidas')]

        final = paralelas_repetidas[(paralelas_repetidas['cod_distri_1']==paralelas_repetidas['cod_distri_2']) & (paralelas_repetidas['nomvtotal_1']==paralelas_repetidas['nomvtotal_2']) & (paralelas_repetidas['generadora_1']==paralelas_repetidas['generadora_2']) ]
        ind_rep_p2=set(final.index)

        ind_rep = set(ind_rep_p1)-set(ind_rep_p2)

        cond1 = mv_brasil.index.isin(ind_rep)
        cond2 = mv_brasil['incidencia'].isna()
        cond3 = mv_brasil['exclusion'].str.contains(r'\[5\]', na=False)
        mv_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_brasil['incidencia'] + " - 5. Via repetida"
        mv_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "5. Via repetida"

    if key == 6:     
    
        #6 CONTINUIDAD EN PRINCIPAL (NOMBRE) 

        #copia malla
        copia_malla=mv_brasil.copy()
        #Filtro
        filtro = mv_brasil[(mv_brasil['cod_estado']==dep) & (mv_brasil['cod_mun']==prov) & (mv_brasil['nomvtotal'].notna()) & (~mv_brasil['nomvtotal'].str.contains('S/N', na=False)) ].copy()
        #Agrupar por cod_distri y nomvtotal
        union = filtro[['cod_distri','nomvtotal','geom']].dissolve(by=['cod_distri','nomvtotal'])
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
            gdf = repetidos[(repetidos['cod_distri']==a[0]) & (repetidos['nomvtotal']==a[1])]
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
        puntos_sep = pd.concat([repetidos.reset_index(drop=False)[['cod_distri','nomvtotal','punto_inicio1','geom','grupo']].rename(columns={'punto_inicio1': 'punto'}), repetidos.reset_index(drop=False)[['cod_distri','nomvtotal','punto_final1','geom','grupo']].rename(columns={'punto_final1': 'punto'})], axis=0)
        #Cuantas lineas tocan cada punto
        agrupados = puntos_sep.groupby(['cod_distri', 'nomvtotal','punto','grupo']).size().reset_index(name='count')
        #Obtener solo puntos extremos o sea solo puntos 1
        unos=agrupados[agrupados['count']==1][['cod_distri', 'nomvtotal','punto','grupo']]
            #2. rotondas trayecto cerrados
            #3 o +. Uniones de vias como callejones o salidas de puentes o de autopistas grandes
        #----------------------
        #Grupos existentes con extremos  
        group_counts = unos.groupby(['cod_distri', 'nomvtotal'])['grupo'].nunique()

        # Filtrar solo aquellas combinaciones donde coddist y nomvvtotal tiene multiples grupos (quitar trayectorias cerradas)
        combinations_with_multiple_groups = group_counts[group_counts > 1].index

        # Filtrar el DataFrame original para obtener las combinaciones y sus ggrupos con sus puntos extremos
        filtro_uno_mas_grupos = unos[unos.set_index(['cod_distri', 'nomvtotal']).index.isin(combinations_with_multiple_groups)]

        #Puntos agrupados (en un solo campo) por cod_distri,nomvtotal y grupo (externos)
        puntos_agrupados = filtro_uno_mas_grupos.groupby(['cod_distri', 'nomvtotal', 'grupo']).agg(
            puntos=('punto',list)  # Crear una lista de puntos
        ).reset_index()
        #obtener de repetidos los trayectos que resultan de los filtros anteriores (lineas)
        ultimo_filtro=repetidos[repetidos.set_index(['cod_distri','nomvtotal','grupo']).index.isin(puntos_agrupados.set_index(['cod_distri','nomvtotal','grupo']).index)][['cod_distri','nomvtotal','geom','grupo']]  
        #Unir todas las geometrias que se tocan en una (Multilinestring) para comparar la cercania de una geometria con todos los puntos de los otros grupos
        ultima_union = ultimo_filtro.dissolve(by=['cod_distri','nomvtotal','grupo'])
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
        gdf = gpd.GeoDataFrame(marcas, columns=['cod_distri', 'nomvtotal', 'geom'], geometry='geom')        
        gdf.set_crs("EPSG:4326", allow_override=True, inplace=True)
        #-
        result = gpd.sjoin(filtro, gdf, how="left", predicate='intersects')
        result = result[(result['cod_distri_left'] == result['cod_distri_right']) & (result['nomvtotal_left'] == result['nomvtotal_right'])].copy()
        #--


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
            return atan2(dy, dx)

        filtro['punto_inicio'] = filtro['geom'].apply(get_start_point)
        filtro['punto_fin'] = filtro['geom'].apply(get_end_point)
        filtro['orientacion'] = filtro.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        filtroindices=filtro.loc[list(result.index.unique())]
        joined = gpd.sjoin(filtroindices, filtro, how='left', predicate='intersects', lsuffix='1', rsuffix='2')
        joined = joined[joined['id_1']!=joined['id_2']]

        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < radians(30):
                return 'Paralelas'
            elif radians(70) < diferencia_orientacion < radians(110):
                return 'Perpendiculares'
            elif radians(150) < diferencia_orientacion < radians(210):#----------------#
                return 'Paralelas invertidas'
            else:
                return 'No son paralelas ni perpendiculares'

        joined['relacion'] = joined['diferencia_orientacion'].apply(clasificar_relacion)
        paralelas_continuidad = joined[(joined['relacion'] == 'Paralelas') | (joined['relacion'] == 'Paralelas invertidas')].copy()

        Marcafinal = set(paralelas_continuidad[(paralelas_continuidad['cod_distri_1']==paralelas_continuidad['cod_distri_2']) & (paralelas_continuidad['nomvtotal_1']!=paralelas_continuidad['nomvtotal_2'])][['id_1','cod_estado_1','cod_mun_1','cod_distri_1','nomvtotal_1','id_2','cod_estado_2','cod_mun_2','cod_distri_2','nomvtotal_2']].index)

        cond1 = mv_brasil.index.isin(Marcafinal)
        cond2 = mv_brasil['incidencia'].isna()
        cond3 = mv_brasil['exclusion'].str.contains(r'\[7\]', na=False)
        mv_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_brasil['incidencia'] + " - 6. Revisar Continuidad"
        mv_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "6. Revisar Continuidad" 

    if key == 7: 
    
        #7 salto generadora
        filtro = mv_brasil[(mv_brasil['cod_estado']==dep) & (mv_brasil['cod_mun']==prov) & (mv_brasil['generadora'].notna()) & (mv_brasil['nomvtotal'].notna()) & (~mv_brasil['nomvtotal'].str.contains('S/N', na=False))].copy()

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
            return atan2(dy, dx)

        # Aplicar función a cada geometría (asumiendo que son LineStrings)
        filtro['punto_inicio'] = filtro['geom'].apply(get_start_point)
        filtro['punto_fin'] = filtro['geom'].apply(get_end_point)
        filtro['orientacion'] = filtro.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        def duplicar_por_valores_3(df, columna):
            df['valor_menor']=None
            df['valor_mayor']=None
            for row in df.itertuples():
                valores = row._asdict()[columna].split('|')
                valores_ordenados = sorted(set(list(map(int, valores))))
                valores_unicos=[valores_ordenados[0],valores_ordenados[-1]]
                df.at[row.Index,'valor_menor'] = valores_unicos[0]
                df.at[row.Index,'valor_mayor'] = valores_unicos[1]
            return df

        filtro = duplicar_por_valores_3(filtro, 'generadora')

        filtro['valor_menor'] = pd.to_numeric(filtro['valor_menor'])
        filtro['valor_mayor'] = pd.to_numeric(filtro['valor_mayor'])

        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
        joined = joined[joined['id_1'] != joined['id_2']]
        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < radians(30):
                return 'Paralelas'
            elif radians(70) < diferencia_orientacion < radians(110):
                return 'Perpendiculares'
            elif radians(150) < diferencia_orientacion < radians(210):#----------------#
                return 'Paralelas invertidas'
            else:
                return 'No son paralelas ni perpendiculares'

        joined['relacion'] = joined['diferencia_orientacion'].apply(clasificar_relacion)


        joined.loc[(joined['punto_inicio_1'].intersects(joined['punto_inicio_2'])|(joined['punto_inicio_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'inicio'
        joined.loc[(joined['punto_fin_1'].intersects(joined['punto_inicio_2'])|(joined['punto_fin_1'].intersects(joined['punto_fin_2'])),'conexion')]= 'fin'

        #------------
        paralelas_generadoras = joined[(joined['relacion'] == 'Paralelas') | (joined['relacion'] == 'Paralelas invertidas')]
        paralelas_generadoras_via = paralelas_generadoras[paralelas_generadoras['nomvtotal_1'] == paralelas_generadoras['nomvtotal_2']].copy()

        paralelas_generadoras_via_fin = paralelas_generadoras_via[paralelas_generadoras_via['conexion']=='fin'].copy()
        paralelas_generadoras_via_fin['resta']=paralelas_generadoras_via_fin['valor_mayor_1']-paralelas_generadoras_via_fin['valor_menor_2']

        paralelas_final=paralelas_generadoras_via_fin[~(paralelas_generadoras_via_fin['resta']==0) & ~(paralelas_generadoras_via_fin['resta']==-100)]

        id_gen_m=paralelas_final.index

        cond1 = mv_brasil.index.isin(id_gen_m)
        cond2 = mv_brasil['incidencia'].isna()
        cond3 = mv_brasil['exclusion'].str.contains(r'\[5\]', na=False)
        mv_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_brasil['incidencia'] + " - 7. Salto generadora"
        mv_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "7. Salto generadora"

    if key ==8:
            
        #8 Error apuntamiento
        filtro = mv_brasil[(mv_brasil['cod_estado']==dep) & (mv_brasil['cod_mun']==prov) & (~mv_brasil['nomvtotal'].str.contains('S/N', na=False))].copy()

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
            return atan2(dy, dx)

        # Aplicar función a cada geometría (asumiendo que son LineStrings)
        filtro['punto_inicio'] = filtro['geom'].apply(get_start_point)
        filtro['punto_fin'] = filtro['geom'].apply(get_end_point)
        filtro['orientacion'] = filtro.apply(lambda row: calculate_azimuth(row['punto_inicio'], row['punto_fin']), axis=1)

        # Unir el GeoDataFrame consigo mismo para comparar segmentos cercanos o que se intersectan
        joined = gpd.sjoin(filtro, filtro, how='inner', op='intersects', lsuffix='1', rsuffix='2')
        # Filtrar donde no sean la misma línea
        joined = joined[joined['id_1'] != joined['id_2']]

        # Calcular diferencias de orientación
        joined['diferencia_orientacion'] = np.abs(joined['orientacion_1'] - joined['orientacion_2'])

        # Clasificar las relaciones en 'Paralelas', 'Perpendiculares', o 'No son paralelas ni perpendiculares'
        def clasificar_relacion(diferencia_orientacion):
            if diferencia_orientacion < radians(30):
                return 'Paralelas'
            elif radians(70) < diferencia_orientacion < radians(110):
                return 'Perpendiculares'
            elif radians(150) < diferencia_orientacion < radians(210):#----------------#
                return 'Paralelas invertidas'
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
        cond1 = mv_brasil.index.isin(errores_apuntamiento)
        cond2 = mv_brasil['incidencia'].isna()
        cond3 = mv_brasil['exclusion'].str.contains(r'\[8\]', na=False)
        mv_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_brasil['incidencia'] + " - 8. Error apuntamiento"
        mv_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "8. Error apuntamiento"
    
    if key ==9 :
    
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

        def min_max_placa(group):
            min_placa = group.loc[group['placa'].idxmin()]
            max_placa = group.loc[group['placa'].idxmax()]
            return pd.Series({
                'min_placa': min_placa['placa'],
                'ind_pl_min': min_placa['ind_pl'],
                'max_placa': max_placa['placa'],
                'ind_pl_max': max_placa['ind_pl']
            })

        filtro = placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov)].dropna(subset=['nomvtotal','generadora'])
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=2))
            resultados.append([row.Index,candidates[0],candidates[1]])
        copia_malla = mv_brasil.copy()
        copia_malla['list_generadora']=copia_malla['generadora'].apply(lambda x: [''] if x is None else x.split('|'))
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno','mv_dos'])
        combo=[]
        for row in resultados_df.itertuples(index=False):
            if ((placas_brasil.at[row[0], 'nomvtotal']==copia_malla.at[row[1], 'nomvtotal']) and (placas_brasil.at[row[0], 'generadora'] in copia_malla.at[row[1], 'list_generadora'])):
                combo.append([row[1],row[0],placas_brasil.at[row[0],'placa']])
            elif ((placas_brasil.at[row[0], 'nomvtotal']==copia_malla.at[row[2], 'nomvtotal']) and (placas_brasil.at[row[0], 'generadora'] in copia_malla.at[row[2], 'list_generadora'])):
                combo.append([row[2],row[0],placas_brasil.at[row[0],'placa']])
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
            az_mv = calcular_azimuth(get_start_point(mv_brasil.loc[row[0],'geom']),get_end_point(mv_brasil.loc[row[0],'geom']))
            az_mv = radians((degrees(az_mv)+360)%360)
            az_p = calcular_azimuth(placas_brasil.loc[row[2],'geom'],placas_brasil.loc[row[4],'geom'])
            az_p = radians((degrees(az_p)+360)%360)
            if abs(az_mv-az_p)>radians(100):
                mala_orientacion.add(row[0])
        par_fin=par_fin[~par_fin['ind_mv'].isin(mala_orientacion)]
        for row in par_fin.itertuples(index = False):
            az_mv = calcular_azimuth(get_start_point(mv_brasil.loc[row[0],'geom']),get_end_point(mv_brasil.loc[row[0],'geom']))
            az_mv = radians((degrees(az_mv)+360)%360)
            az_p = calcular_azimuth(placas_brasil.loc[row[2],'geom'],placas_brasil.loc[row[4],'geom'])
            az_p = radians((degrees(az_p)+360)%360)
            if abs(az_mv-az_p)>radians(100):
                mala_orientacion.add(row[0])
        #MARCAR 
        cond1 = mv_brasil.index.isin(mala_orientacion)
        cond2 = mv_brasil['incidencia'].isna()
        cond3 = mv_brasil['exclusion'].str.contains(r'\[9\]', na=False)
        mv_brasil.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_brasil['incidencia'] + " - 9. Invertir vector"
        mv_brasil.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "9. Invertir vector"

    if key ==10 :
        #10
        filtro = placas_brasil[(placas_brasil['cod_estado']==dep) & (placas_brasil['cod_mun']==prov)].dropna(subset=['nomvtotal','generadora'])
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=2))
            resultados.append([row.Index,candidates[0],candidates[1]])
        copia_malla = mv_brasil.copy()
        copia_malla['list_generadora']=copia_malla['generadora'].apply(lambda x: [''] if x is None else x.split('|'))
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno','mv_dos'])
        combo=[]
        for row in resultados_df.itertuples(index=False):
            if ((placas_brasil.at[row[0], 'nomvtotal']==copia_malla.at[row[1], 'nomvtotal']) and (placas_brasil.at[row[0], 'generadora'] in copia_malla.at[row[1], 'list_generadora'])):
                combo.append([row[1],placas_brasil.at[row[0],'placa']])
            elif ((placas_brasil.at[row[0], 'nomvtotal']==copia_malla.at[row[2], 'nomvtotal']) and (placas_brasil.at[row[0], 'generadora'] in copia_malla.at[row[2], 'list_generadora'])):
                combo.append([row[2],placas_brasil.at[row[0],'placa']])
        combo_df = pd.DataFrame(combo,columns=['ind_mv','placa'])
        combo_df['placa']= pd.to_numeric(combo_df['placa'])
        impar= combo_df[(combo_df['placa'] % 2 == 1)]
        par= combo_df[(combo_df['placa'] % 2 == 0)]
        result_par = par.groupby('ind_mv')['placa'].agg(['min', 'max'])
        result_impar = impar.groupby('ind_mv')['placa'].agg(['min', 'max'])
        result_par['rangopar']=result_par['min'].astype(str) +'-'+result_par['max'].astype(str)
        result_impar['rangoimpar']=result_impar['min'].astype(str) +'-'+result_impar['max'].astype(str)
        mv_brasil.loc[result_impar.index, 'rangoimpar']=result_impar['rangoimpar']
        mv_brasil.loc[result_par.index, 'rangopar']=result_par['rangopar']
    
    return mv_brasil
    
def Brasil_validar_mv(engine, mavvial, placas, texto_filtro, seleccionados):

    mifiltro=texto_filtro #####AQUI VA EL FILTRO#####
    partes = mifiltro.split(',')
    dep=partes[0]
    prov=partes[1]

    campos_1 = 'id,geom,nom_estado,nom_mun,nom_distri,tipovia,nomvia,nomvtotal,atipico'
    campos_2 = 'id,geom,id_capa,atipico'
    campos_3 = 'id,geom,cod_estado,cod_mun,nomvia,generadora,atipico'
    campos_4 = 'id,geom,cod_estado,cod_mun,cod_distri,nomvtotal,generadora,atipico'
    campos_5 = 'id,geom,cod_estado,cod_mun,cod_distri,nomvtotal,generadora,atipico'  
    campos_6 = 'id,geom,cod_estado,cod_mun,cod_distri,nomvtotal,atipico'
    campos_7 = 'id,geom,cod_estado,cod_mun,cod_distri,nomvtotal,generadora,atipico'   
    campos_8 = 'id,geom,cod_estado,cod_mun,cod_distri,nomvtotal,generadora,atipico'
    campos_9 = 'id,geom,cod_estado,cod_mun,cod_distri,nomvtotal,generadora,atipico'
    campos_10 = 'id,geom,cod_estado,cod_mun,cod_distri,tipovia,nomvia,nomvtotal,generadora,atipico'
    
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

    sql = f"SELECT {final_fields} FROM {mavvial} WHERE cod_estado = '{dep}' AND cod_mun = '{prov}';"
    mv_brasil = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
    mv_brasil['incidencia'] = None   
    mv_brasil['rangopar'] = None  
    mv_brasil['rangoimpar'] = None  
    mv_brasil['exclusion'] = mv_brasil['atipico'].apply(
        lambda mi_string: ','.join([f"[{x}]" for x in mi_string.replace(" ", "").split(",")]) 
        if mi_string is not None else None
	)
    
    #Solo se utiliza en 12 por lo qe no se va a mandar como parametro

    
    if (set(seleccionados) - {1,2,3,4,5,6,7,8}) != set():#Que no
        sql=f"SELECT id,geom,cod_estado,cod_mun,cod_distri,tipovia,nomvia,nomvtotal,generadora,placa FROM {placas} WHERE cod_estado = '{dep}' AND cod_mun = '{prov}';"
        placas_brasil = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
        
        if ({9,10} & set(seleccionados)) != set():#Que si
                idx = indexx.Index()
                # Agregar líneas al índice
                for i, geometry in enumerate(mv_brasil.geometry):
                    if geometry is not None:
                        idx.insert(i, geometry.bounds)
        else:
            idx=''

    else:
        placas_brasil=''
        idx=''
        
    for key in seleccionados:   
        mv_brasil = Brasil_mv_incidencia( mv_brasil, placas_brasil, texto_filtro, key,idx)
        
    df_temporal = mv_brasil[['id', 'incidencia', 'rangopar', 'rangoimpar']]
    df_temporal.to_sql('tabla_temporal', con=engine, index=False, if_exists='replace')