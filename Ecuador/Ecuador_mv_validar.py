def Ecuador_QueryValMavvial(mavvial,placas):
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
    UPDATE """ + mavvial + """ SET nom_prov = UPPER(nom_prov) WHERE nom_prov <> UPPER(nom_prov);
    UPDATE """ + mavvial + """ SET nom_can = UPPER(nom_can) WHERE nom_can <> UPPER(nom_can);
    UPDATE """ + mavvial + """ SET nom_parroq = UPPER(nom_parroq) WHERE nom_parroq <> UPPER(nom_parroq);
    UPDATE """ + mavvial + """ SET nomvia = UPPER(nomvia) WHERE nomvia <> UPPER(nomvia);
    UPDATE """ + mavvial + """ SET nomvtotal = UPPER(nomvtotal) WHERE nomvtotal <> UPPER(nomvtotal);
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX REEMPLAZAR SIMBOLOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/  
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX REEMPLAZAR SIMBOLOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/  
    UPDATE """ + mavvial + """ SET nom_prov = regexp_replace(nom_prov, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_prov ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + mavvial + """ SET nom_can = regexp_replace(nom_can, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_can ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';
    
    UPDATE """ + mavvial + """ SET nom_parroq = regexp_replace(nom_parroq, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nom_parroq ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]';

    UPDATE """ + mavvial + """ SET nomvia = regexp_replace(nomvia, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nomvia ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]'
    AND nomvia != 'S/N';
    
    UPDATE """ + mavvial + """ SET nomvtotal = regexp_replace(nomvtotal, '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]', ' ', 'g')
    WHERE nomvtotal ~ '[\\|\\!"#@$%&/()¿¡¨{}\\[\\]._:,;+\\-*=/¬°]'
    AND nomvtotal != 'S/N';
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX REEMPLAZAR TILDES XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/ 

    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'Á','A') WHERE nomvia LIKE '%Á%';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'É','E') WHERE nomvia LIKE '%É%';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'Í','I') WHERE nomvia LIKE '%Í%';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'Ó','O') WHERE nomvia LIKE '%Ó%';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'Ú','U') WHERE nomvia LIKE '%Ú%';   

    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'Á','A') WHERE nomvtotal LIKE '%Á%';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'É','E') WHERE nomvtotal LIKE '%É%';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'Í','I') WHERE nomvtotal LIKE '%Í%';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'Ó','O') WHERE nomvtotal LIKE '%Ó%';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'Ú','U') WHERE nomvtotal LIKE '%Ú%'; 
    
    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR ESPACIOS INICIO-FIN XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_prov = TRIM(nom_prov) WHERE nom_prov <> TRIM(nom_prov);
    UPDATE """ + mavvial + """ SET nom_can = TRIM(nom_can) WHERE nom_can <> TRIM(nom_can);
    UPDATE """ + mavvial + """ SET nom_parroq = TRIM(nom_parroq) WHERE nom_parroq <> TRIM(nom_parroq);
    UPDATE """ + mavvial + """ SET nomvia = TRIM(nomvia) WHERE nomvia <> TRIM(nomvia);
    UPDATE """ + mavvial + """ SET nomvtotal = TRIM(nomvtotal) WHERE nomvtotal <> TRIM(nomvtotal);

    /*XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX QUITAR DOBLES ESPACIOS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX*/
    UPDATE """ + mavvial + """ SET nom_prov = REPLACE(nom_prov,'  ',' ') WHERE nom_prov LIKE '%  %';
    UPDATE """ + mavvial + """ SET nom_can = REPLACE(nom_can,'  ',' ') WHERE nom_can LIKE '%  %';
    UPDATE """ + mavvial + """ SET nom_parroq = REPLACE(nom_parroq,'  ',' ') WHERE nom_parroq LIKE '%  %';
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
    
    /*TODO LO QUE SEA PRIMER,PRIMERA,1ER REEMPLAZAR POR NUMEROS*/
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'PRIMERA','1') WHERE nomvia LIKE '%PRIMERA %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'SEGUNDA','2') WHERE nomvia LIKE '%SEGUNDA %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'TERCERA','3') WHERE nomvia LIKE '%TERCERA %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'CUARTA','4') WHERE nomvia LIKE '%CUARTA %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'QUINTA','5') WHERE nomvia LIKE '%QUINTA %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'SEXTA','6') WHERE nomvia LIKE '%SEXTA %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'SEPTIMA','7') WHERE nomvia LIKE '%SEPTIMA %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'OCTAVA','8') WHERE nomvia LIKE '%OCTAVA %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'NOVENA','9') WHERE nomvia LIKE '%NOVENA %';
    
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'PRIMERA','1') WHERE nomvtotal LIKE '%PRIMERA %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'SEGUNDA','2') WHERE nomvtotal LIKE '%SEGUNDA %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'TERCERA','3') WHERE nomvtotal LIKE '%TERCERA %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'CUARTA','4') WHERE nomvtotal LIKE '%CUARTA %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'QUINTA','5') WHERE nomvtotal LIKE '%QUINTA %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'SEXTA','6') WHERE nomvtotal LIKE '%SEXTA %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'SEPTIMA','7') WHERE nomvtotal LIKE '%SEPTIMA %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'OCTAVA','8') WHERE nomvtotal LIKE '%OCTAVA %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'NOVENA','9') WHERE nomvtotal LIKE '%NOVENA %';

    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'PRIMER','1') WHERE nomvia LIKE '%PRIMER %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'PRIMERO','1') WHERE nomvia LIKE '%PRIMERO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'SEGUNDO','2') WHERE nomvia LIKE '%SEGUNDO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'TERCERO','3') WHERE nomvia LIKE '%TERCERO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'CUARTO','4') WHERE nomvia LIKE '%CUARTO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'QUINTO','5') WHERE nomvia LIKE '%QUINTO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'SEXTO','6') WHERE nomvia LIKE '%SEXTO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'SEPTIMO','7') WHERE nomvia LIKE '%SEPTIMO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'OCTAVO','8') WHERE nomvia LIKE '%OCTAVO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'NOVENO','9') WHERE nomvia LIKE '%NOVENO %';
    
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'PRIMER','1') WHERE nomvtotal LIKE '%PRIMER %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'PRIMERO','1') WHERE nomvtotal LIKE '%PRIMERO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'SEGUNDO','2') WHERE nomvtotal LIKE '%SEGUNDO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'TERCERO','3') WHERE nomvtotal LIKE '%TERCERO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'CUARTO','4') WHERE nomvtotal LIKE '%CUARTO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'QUINTO','5') WHERE nomvtotal LIKE '%QUINTO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'SEXTO','6') WHERE nomvtotal LIKE '%SEXTO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'SEPTIMO','7') WHERE nomvtotal LIKE '%SEPTIMO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'OCTAVO','8') WHERE nomvtotal LIKE '%OCTAVO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'NOVENO','9') WHERE nomvtotal LIKE '%NOVENO %';

    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'UNO','1') WHERE nomvia LIKE '%UNO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'DOS','2') WHERE nomvia LIKE '%DOS %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'TRES','3') WHERE nomvia LIKE '%TRES %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'CUATRO','4') WHERE nomvia LIKE '%CUATRO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'CINCO','5') WHERE nomvia LIKE '%CINCO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'SEIS','6') WHERE nomvia LIKE '%SEIS %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'SIETE','7') WHERE nomvia LIKE '%SIETE %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'OCHO','8') WHERE nomvia LIKE '%OCHO %';
    UPDATE """ + mavvial + """ SET nomvia = REPLACE(nomvia,'NUEVE','9') WHERE nomvia LIKE '%NUEVE %';
    
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'UNO','1') WHERE nomvtotal LIKE '%UNO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'DOS','2') WHERE nomvtotal LIKE '%DOS %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'TRES','3') WHERE nomvtotal LIKE '%TRES %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'CUATRO','4') WHERE nomvtotal LIKE '%CUATRO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'CINCO','5') WHERE nomvtotal LIKE '%CINCO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'SEIS','6') WHERE nomvtotal LIKE '%SEIS %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'SIETE','7') WHERE nomvtotal LIKE '%SIETE %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'OCHO','8') WHERE nomvtotal LIKE '%OCHO %';
    UPDATE """ + mavvial + """ SET nomvtotal = REPLACE(nomvtotal,'NUEVE','9') WHERE nomvtotal LIKE '%NUEVE %';
    
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

def Ecuador_mv_incidencia(mv_ecuador, placas_ecuador, texto_filtro, key,idx):

    mifiltro=texto_filtro #####AQUI VA EL FILTRO#####
    partes = mifiltro.split(',')
    if partes:
        dep=partes[0]
        prov=partes[1]
     
    if key ==1 :
        # 1. Validar registro con caracteres
        id_excp = list(mv_ecuador.loc[mv_ecuador['exclusion'].str.contains(r'\[1\]', na=False),'id'])
        # Expresión regular para caracteres especiales
        simbolos = r'[|!"#@$%&/()¿¡¨{}\[\]._:,;+\-*=/¬°]'

        # Función para marcar la inconsistencia si hay caracteres especiales en alguna columna específica
        def marcar_simbolos(row):
            if row['nomvia'] != 'S/N':
                columnas = ['nom_prov', 'nom_can', 'nom_parroq', 'tipovia', 'nomvia', 'nomvtotal']
                for col in columnas:
                    if pd.notna(row[col]) and re.search(simbolos, row[col]) and (row['id'] not in id_excp):
                        return '1. Validar registro con caracteres - '
            return None

        # Aplicar la función para marcar incidencia
        mv_ecuador['incidencia'] = mv_ecuador.apply(marcar_simbolos, axis=1)
    
    if key == 2:
        #2 id_capa duplicado
        frecuencias = mv_ecuador['id_capa'].value_counts().reset_index()
        valor_dict = frecuencias[frecuencias['count'] > 1].set_index('id_capa')['count'].to_dict()
        id_excp = list(mv_ecuador.loc[mv_ecuador['exclusion'].str.contains(r'\[2\]', na=False),'id'])
        mv_ecuador['incidencia'] = mv_ecuador.apply(
            lambda row: f"{row['incidencia']} - 2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is not None and row['id_capa'] in valor_dict and row['id'] not in id_excp else 
            f"2. id_capa duplicado {valor_dict[row['id_capa']]} veces" if row['incidencia'] is  None and row['id_capa'] in valor_dict and row['id'] not in id_excp else
            row['incidencia'],
            axis=1
        )

    if key == 3:    
        #4 generadora (generadora) es vacio

        filtro = mv_ecuador[(mv_ecuador['cod_prov']==dep) & (mv_ecuador['cod_can']==prov)].copy()

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
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
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

        
        joined['generadora_1'] = joined['generadora_1'].str.replace(r'\D', '', regex=True)
        joined['generadora_1'] = pd.to_numeric(joined['generadora_1'], errors='coerce')
        joined['generadora_2'] = joined['generadora_2'].str.replace(r'\D', '', regex=True)
        joined['generadora_2'] = pd.to_numeric(joined['generadora_2'], errors='coerce')



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
        SG = paralelas_generadora[(paralelas_generadora['nomvia_1'].isna()) & (paralelas_generadora['longitud_1'] > 15)]

        
        id_par_sg = SG[(SG['nomvia_2'].notna())].index.unique()
        id_cll = joined[(joined['nomvia_1'].isna()) & (joined['validacion_call'] == 0)].index.unique()
        nomvianulo = set(id_par_sg) - set(id_cll)


        cond1 = mv_ecuador.index.isin(nomvianulo)
        cond2 = mv_ecuador['incidencia'].isna()
        cond3 = mv_ecuador['exclusion'].str.contains(r'\[4\]', na=False)
        mv_ecuador.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_ecuador['incidencia'] + " - 4. Nombre de vía vacío"
        mv_ecuador.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "4. Nombre de vía vacío"



    if key == 4:    
        #4 generadora (generadora) es vacio

        filtro = mv_ecuador[(mv_ecuador['cod_prov']==dep) & (mv_ecuador['cod_can']==prov)].copy()

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
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
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

        
        joined['generadora_1'] = joined['generadora_1'].str.replace(r'\D', '', regex=True)
        joined['generadora_1'] = pd.to_numeric(joined['generadora_1'], errors='coerce')
        joined['generadora_2'] = joined['generadora_2'].str.replace(r'\D', '', regex=True)
        joined['generadora_2'] = pd.to_numeric(joined['generadora_2'], errors='coerce')



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

        cond1 = mv_ecuador.index.isin(generadoranulo)
        cond2 = mv_ecuador['incidencia'].isna()
        cond3 = mv_ecuador['exclusion'].str.contains(r'\[4\]', na=False)
        mv_ecuador.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_ecuador['incidencia'] + " - 4. Generadora vacia"
        mv_ecuador.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "4. Generadora vacia"

    if key == 5:     
        #5 MV REPETIDAS

        #P1
        copia_malla=mv_ecuador[(mv_ecuador['cod_prov']==dep) & (mv_ecuador['cod_can']==prov) &(~mv_ecuador['nomvtotal'].str.contains('S/N', na=False))].dropna(subset=['cod_prov', 'cod_can','cod_parroq','nomvtotal','generadora']).reset_index(drop=False).set_index(['cod_prov','cod_can','cod_parroq','nomvtotal','generadora']).sort_index()
        #Agregarlongitud
        copia_malla['longitud'] = copia_malla.to_crs(epsg=3857).geometry.length
        mallamas15=copia_malla[copia_malla['longitud']>15]
        repeated_indices = mallamas15.index.value_counts()
        repeated_indices = repeated_indices[repeated_indices > 1].index
        ind_rep_p1 = list(copia_malla[copia_malla.index.isin(repeated_indices)]['index'])


        #P2
        filtro = mv_ecuador[(mv_ecuador['cod_prov']==dep) & (mv_ecuador['cod_can']==prov) & (~mv_ecuador['nomvtotal'].str.contains('S/N', na=False))].copy()
        
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
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
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


        joined['generadora_1'] = joined['generadora_1'].str.replace(r'\D', '', regex=True)
        joined['generadora_1'] = pd.to_numeric(joined['generadora_1'], errors='coerce')
        joined['generadora_2'] = joined['generadora_2'].str.replace(r'\D', '', regex=True)
        joined['generadora_2'] = pd.to_numeric(joined['generadora_2'], errors='coerce')

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

        vias_rep = joined[(joined['nomvtotal_1'] == joined['nomvtotal_2']) & (joined['generadora_1'] == joined['generadora_2'])].copy()
        vias_rep_con_t=vias_rep[(vias_rep['validacion_t']==2)]

        ind_rep_p2=vias_rep_con_t.index
        ind_rep = set(ind_rep_p1)-set(ind_rep_p2)

        cond1 = mv_ecuador.index.isin(ind_rep)
        cond2 = mv_ecuador['incidencia'].isna()
        cond3 = mv_ecuador['exclusion'].str.contains(r'\[5\]', na=False)
        mv_ecuador.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_ecuador['incidencia'] + " - 5. Via repetida"
        mv_ecuador.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "5. Via repetida"

    if key == 6:     
        #6 SALTOS EN PRINCIPAL (nomvtotal) 
        filtro = mv_ecuador[(mv_ecuador['cod_prov']==dep) & (mv_ecuador['cod_can']==prov)].copy()


        #Lista de exclusion
        id_excp = list(mv_ecuador.loc[mv_ecuador['exclusion'].str.contains(r'\[6\]', na=False),'id'])
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
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
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
        # Filtrar por condición: principal1 != principal2 y quitar exclusiones

        precondicion = paralelas[(paralelas['nomvtotal_1'] != paralelas['nomvtotal_2']) & ~(paralelas['id_1'].isin(id_excp))].copy()####
        preprecondicion = precondicion[~((precondicion['longitud_1'] < 15) | (precondicion['longitud_2'] < 15))]
        condicion = preprecondicion[~((preprecondicion['nomvtotal_1'] != preprecondicion['nomvtotal_2']) & (preprecondicion['cod_parroq_1'] != preprecondicion['cod_parroq_2']))].copy()####
        # Actualizar el campo de incidencia
        condicion['incidencia_1'] = condicion['incidencia_1'].fillna('') + ' - 6. Revisar continuidad ' #CAMBIAR A incidencia DE AQUI PARA ABAJO
        # Eliminar duplicados en la columna 'id_1'
        condicion = condicion.drop_duplicates(subset=['id_1'])
        # Realizar el merge entre mv_ecuador y condicion
        mv_ecuador_actualizado = mv_ecuador.merge(condicion[['id_1', 'incidencia_1']], left_on='id', right_on='id_1', how='left')
        # Actualizar la columna 'incidencia' solo donde 'incidencia_1' tenga valores
        mv_ecuador_actualizado['incidencia'] = mv_ecuador_actualizado['incidencia_1'].combine_first(mv_ecuador_actualizado['incidencia'])
        # Eliminar las columnas auxiliares ('id_1' y 'incidencia_1') si ya no las necesitas
        mv_ecuador_actualizado = mv_ecuador_actualizado.drop(columns=['id_1', 'incidencia_1'])
        # Guardar los cambios en el DataFrame original
        mv_ecuador = mv_ecuador_actualizado.copy()

    if key == 7: 
        #7 salto generadora
        filtro = mv_ecuador[(mv_ecuador['cod_prov']==dep) & (mv_ecuador['cod_can']==prov) & (~mv_ecuador['nomvtotal'].str.contains('S/N', na=False))].copy()
        
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
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
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
        joined['generadora_1'] = joined['generadora_1'].str.replace(r'\D', '', regex=True)
        joined['generadora_1'] = pd.to_numeric(joined['generadora_1'], errors='coerce')
        joined['generadora_2'] = joined['generadora_2'].str.replace(r'\D', '', regex=True)
        joined['generadora_2'] = pd.to_numeric(joined['generadora_2'], errors='coerce')

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

        #quitarTs y lineas menores a 15 metros 
        paralelas_generadoras_via=paralelas_generadoras_via[~((paralelas_generadoras_via['resta']==0) & (paralelas_generadoras_via['validacion_t']==2))]
        paralelas_generadoras_via = paralelas_generadoras_via[~(((paralelas_generadoras_via['longitud_1'] < 15) | (paralelas_generadoras_via['longitud_2'] < 15)) & (paralelas_generadoras_via['resta'] == 0))]
        #------------------------

        saltos_gen=paralelas_generadoras_via[(paralelas_generadoras_via['resta' ]!=100) & (paralelas_generadoras_via['resta' ]!=-100)].index

        #MARCAR 
        cond1 = mv_ecuador.index.isin(saltos_gen)
        cond2 = mv_ecuador['incidencia'].isna()
        cond3 = mv_ecuador['exclusion'].str.contains(r'\[7\]', na=False)
        mv_ecuador.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_ecuador['incidencia'] + " - 7. Salto generadora"
        mv_ecuador.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "7. Salto generadora"

    if key == 8:
            
        #8 Error apuntamiento
        filtro = mv_ecuador[(mv_ecuador['cod_prov']==dep) & (mv_ecuador['cod_can']==prov)].copy()

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
        joined = gpd.sjoin(filtro, filtro, how='inner', predicate='intersects', lsuffix='1', rsuffix='2')
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
        cond1 = mv_ecuador.index.isin(errores_apuntamiento)
        cond2 = mv_ecuador['incidencia'].isna()
        cond3 = mv_ecuador['exclusion'].str.contains(r'\[8\]', na=False)
        mv_ecuador.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_ecuador['incidencia'] + " - 8. Error apuntamiento"
        mv_ecuador.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "8. Error apuntamiento"



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

        def min_max_placa(group):
            min_placa = group.loc[group['placa'].idxmin()]
            max_placa = group.loc[group['placa'].idxmax()]
            return pd.Series({
                'min_placa': min_placa['placa'],
                'ind_pl_min': min_placa['ind_pl'],
                'max_placa': max_placa['placa'],
                'ind_pl_max': max_placa['ind_pl']
            })

        filtro = placas_ecuador[(placas_ecuador['cod_prov']==dep) & (placas_ecuador['cod_can']==prov)].dropna(subset=['nomvtotal','generadora'])
        resultados=[]
        for row in filtro.itertuples():
            candidates = list(idx.nearest(row.geom.bounds, num_results=2))
            resultados.append([row.Index,candidates[0],candidates[1]])
        copia_malla = mv_ecuador.copy()
        copia_malla['list_generadora']=copia_malla['generadora'].apply(lambda x: [''] if x is None else x.split('|'))
		
        resultados_df = pd.DataFrame(resultados,columns=['placa','mv_uno','mv_dos'])
        combo = []
        for row in resultados_df.itertuples(index=False):
            nomv_placa = str(placas_ecuador.at[row[0], 'nomvtotal'])
            generadora_placa = str(placas_ecuador.at[row[0], 'generadora'])

            # Convertimos list_generadora en una lista de strings usando .split('|')
            list_generadora_1 = str(copia_malla.at[row[1], 'list_generadora']).split('|')
            list_generadora_2 = str(copia_malla.at[row[2], 'list_generadora']).split('|')

            # Verificamos si generadora_placa está dentro de alguna de las partes de list_generadora
            generadora_match_1 = any(generadora_placa in g for g in list_generadora_1)
            generadora_match_2 = any(generadora_placa in g for g in list_generadora_2)

            if nomv_placa == str(copia_malla.at[row[1], 'nomvtotal']) and generadora_match_1:
                combo.append([row[1], row[0], placas_ecuador.at[row[0], 'placa']])
            elif nomv_placa == str(copia_malla.at[row[2], 'nomvtotal']) and generadora_match_2:
                combo.append([row[2], row[0], placas_ecuador.at[row[0], 'placa']])

        combo_df = pd.DataFrame(combo, columns=['ind_mv', 'ind_pl', 'placa'])
        combo_df['placa'] = pd.to_numeric(combo_df['placa'])

		
		
        impar= combo_df[(combo_df['placa'] % 2 == 1)]
        par= combo_df[(combo_df['placa'] % 2 == 0)]

        list_par_uno = par['ind_mv'].value_counts()[par['ind_mv'].value_counts() == 1].index.tolist()
        list_impar_uno = impar['ind_mv'].value_counts()[impar['ind_mv'].value_counts() == 1].index.tolist()

        par = par[~par['ind_mv'].isin(list_par_uno)]
        impar = impar[~impar['ind_mv'].isin(list_impar_uno)]

        par_fin = par.groupby('ind_mv').apply(min_max_placa).reset_index()
        impar_fin = impar.groupby('ind_mv').apply(min_max_placa).reset_index()


        mala_orientacion = set()
        for row in impar_fin.itertuples(index = False):
            az_mv = calcular_azimuth(get_start_point(mv_ecuador.loc[row[0],'geom']),get_end_point(mv_ecuador.loc[row[0],'geom']))
            az_mv = radians((degrees(az_mv)+360)%360)
            az_p = calcular_azimuth(placas_ecuador.loc[row[2],'geom'],placas_ecuador.loc[row[4],'geom'])
            az_p = radians((degrees(az_p)+360)%360)
            if abs(az_mv-az_p)>radians(100):
                mala_orientacion.add(row[0])
        par_fin=par_fin[~par_fin['ind_mv'].isin(mala_orientacion)]
        for row in par_fin.itertuples(index = False):
            az_mv = calcular_azimuth(get_start_point(mv_ecuador.loc[row[0],'geom']),get_end_point(mv_ecuador.loc[row[0],'geom']))
            az_mv = radians((degrees(az_mv)+360)%360)
            az_p = calcular_azimuth(placas_ecuador.loc[row[2],'geom'],placas_ecuador.loc[row[4],'geom'])
            az_p = radians((degrees(az_p)+360)%360)
            if abs(az_mv-az_p)>radians(100):
                mala_orientacion.add(row[0])
        #MARCAR 
        cond1 = mv_ecuador.index.isin(mala_orientacion)
        cond2 = mv_ecuador['incidencia'].isna()
        cond3 = mv_ecuador['exclusion'].str.contains(r'\[9\]', na=False)
        mv_ecuador.loc[cond1 & ~cond2 & ~cond3, 'incidencia'] = mv_ecuador['incidencia'] + " - 9. Invertir vector"
        mv_ecuador.loc[cond1 & cond2 & ~cond3, 'incidencia'] = "9. Invertir vector"








        
    if key == 10:
        # Filtrar mv_ecuador y placas_ecuador
        agrupados = mv_ecuador[
            (mv_ecuador['cod_prov'] == dep) & 
            (mv_ecuador['cod_can'] == prov) & 
            (~mv_ecuador['nomvia'].str.contains('S/N', na=False))
        ][['cod_parroq', 'tipovia', 'nomvia', 'generadora']].dropna().drop_duplicates()
        
        copia_placas = placas_ecuador[
            (placas_ecuador['cod_prov'] == dep) & 
            (placas_ecuador['cod_can'] == prov) & 
            (~placas_ecuador['nomvia'].str.contains('S/N', na=False)) & 
            (placas_ecuador['atipico'].isna())
        ][['cod_parroq', 'tipovia', 'nomvia', 'generadora', 'placa']].dropna()
        
        # Índice para mejorar el rendimiento
        copia_placas['generadora'] = copia_placas['generadora'].astype(str)
        agrupados['generadora'] = agrupados['generadora'].astype(str)
        
        # Merge utilizando una condición más eficiente
        merged = agrupados.merge(copia_placas, on=['cod_parroq', 'tipovia', 'nomvia'], suffixes=('_mavvial', '_placas'))
        merged = merged[merged.apply(lambda x: x['generadora_placas'] in x['generadora_mavvial'], axis=1)]
        
        # Procesar los rangos
        sin_par, sin_impar = set(), set()
        grouped = merged.groupby(['cod_parroq', 'tipovia', 'nomvia', 'generadora_mavvial'])
        
        for (cod_parroq, tipovia, nomvia, generadora), group in grouped:
            placas = group['placa'].astype(str).tolist()
            
            pares = sorted([int(re.sub(r'\D', '', num)) for num in placas if re.sub(r'\D', '', num).isdigit() and int(re.sub(r'\D', '', num)) % 2 == 0])
            impares = sorted([int(re.sub(r'\D', '', num)) for num in placas if re.sub(r'\D', '', num).isdigit() and int(re.sub(r'\D', '', num)) % 2 != 0])
            
            idx = mv_ecuador.index[(mv_ecuador['cod_parroq'] == cod_parroq) & (mv_ecuador['tipovia'] == tipovia) & (mv_ecuador['nomvia'] == nomvia) & (mv_ecuador['generadora'] == generadora)]
            
            if len(pares) > 0:
                mv_ecuador.loc[idx, 'rangopar'] = f"{pares[0]}, {pares[-1]}"
            else:
                sin_par.update(idx)
            
            if len(impares) > 0:
                mv_ecuador.loc[idx, 'rangoimpar'] = f"{impares[0]}, {impares[-1]}"
            else:
                sin_impar.update(idx)
        
        # Marcar los que no tienen rango
        mv_ecuador.loc[mv_ecuador.index.isin(sin_par), 'rangopar'] = "Sin rango par"
        mv_ecuador.loc[mv_ecuador.index.isin(sin_impar), 'rangoimpar'] = "Sin rango impar"

    return mv_ecuador

     
def Ecuador_validar_mv(engine, mavvial, placas, texto_filtro, seleccionados):

    mifiltro=texto_filtro #####AQUI VA EL FILTRO#####
    partes = mifiltro.split(',')
    if partes:

        dep=partes[0]
        prov=partes[1]
    
    campos_1 = 'id,geom,nom_prov,nom_can,nom_parroq,tipovia,nomvia,nomvtotal,atipico'
    campos_2 = 'id,geom,id_capa,atipico'
    campos_3 = 'id,geom,cod_prov,cod_can,nomvia,generadora,atipico'
    campos_4 = 'id,geom,cod_prov,cod_can,generadora,atipico'
    campos_5 = 'id,geom,cod_prov,cod_can,cod_parroq,nomvtotal,generadora,atipico'  
    campos_6 = 'id,geom,cod_prov,cod_can,cod_parroq,nomvtotal,atipico'
    campos_7 = 'id,geom,cod_prov,cod_can,cod_parroq,nomvtotal,generadora,atipico'   
    campos_8 = 'id,geom,cod_prov,cod_can,cod_parroq,nomvtotal,generadora,atipico'
    campos_9 = 'id,id_capa,geom,cod_prov,cod_can,cod_parroq,tipovia,nomvia,nomvtotal,generadora,atipico'
    campos_10 = 'id,geom,cod_prov,cod_can,cod_parroq,tipovia,nomvia,generadora,atipico'
    
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

    sql = f"SELECT {final_fields} FROM {mavvial} WHERE cod_prov = '{dep}' AND cod_can = '{prov}';"
    mv_ecuador = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
    mv_ecuador['incidencia'] = None   
    mv_ecuador['rangopar'] = None  
    mv_ecuador['rangoimpar'] = None  
    mv_ecuador['exclusion'] = mv_ecuador['atipico'].apply(
        lambda mi_string: ','.join([f"[{x}]" for x in mi_string.replace(" ", "").split(",")]) 
        if mi_string is not None else None
	)                 
            
    if (set(seleccionados) - {1,2,3,4,5,6,7,8}) != set(): #Que no
        sql=f"SELECT id,geom,cod_prov,cod_can,cod_parroq,tipovia,nomvia,nomvtotal,generadora,placa,atipico FROM {placas} WHERE cod_prov = '{dep}' AND cod_can = '{prov}';"
        placas_ecuador = gpd.read_postgis(sql, engine, geom_col='geom',crs= 'EPSG:4326')
    
        if ({9} & set(seleccionados)) != set():#Que si
            idx = indexx.Index()
            #Agregar líneas al índice
            for i, geometry in enumerate(mv_ecuador.geometry):
                if geometry is not None:
                    idx.insert(i, geometry.bounds)
        else:
            idx=''
    else:
        placas_ecuador=''
        idx=''
    
    for key in seleccionados:
        mv_ecuador = Ecuador_mv_incidencia(mv_ecuador, placas_ecuador, texto_filtro, key,idx)
    
    df_temporal = mv_ecuador[['id', 'incidencia', 'rangopar', 'rangoimpar']]
    df_temporal.to_sql('tabla_temporal', con=engine, index=False, if_exists='replace')