import os
import geopandas as gpd
from sqlalchemy import create_engine
import fiona

def Chile_QueryExpCapa(engine,tabla,carpeta_final):

    if tabla[0:8] == 'distrito':
        #print('si entre')
        print(tabla.upper())

        shapefile_name = "distritos"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "cod_dep":"VARCHAR(10)",
            "nom_dep":"VARCHAR(100)",
            "cod_prov":"VARCHAR(10)",
            "nom_prov":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "observ":"VARCHAR(30)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "cod_dep": 'str:10',
                "nom_dep": 'str:100',
                "cod_prov": 'str:10',
                "nom_prov": 'str:100',
                "cod_distri": 'str:10',
                "nom_distri": 'str:100',
                "observ": 'str:30',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }
    
    elif tabla[0:12] == 'departamento':
        print(tabla.upper())    
        shapefile_name = "departamentos"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "cod_dep":"VARCHAR(10)",
            "nom_dep":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "cod_dep": 'str:10',
                "nom_dep": 'str:100',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }
            
    elif tabla[0:11] == 'hidrografia':
        print(tabla.upper())
        
        shapefile_name = "hidrografia"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "nombre":"VARCHAR(100)",
            "cod_dep":"VARCHAR(10)",
            "nom_dep":"VARCHAR(100)",
            "cod_prov":"VARCHAR(10)",
            "nom_prov":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "nombre": 'str:100',
                "cod_dep": 'str:10',
                "nom_dep": 'str:100',
                "cod_prov": 'str:10',
                "nom_prov": 'str:100',
                "cod_distri": 'str:10',
                "nom_distri": 'str:100',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }

            
    elif tabla[0:7] == 'manzana':
        print(tabla.upper())
        
        shapefile_name = "manzanas"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "cod_mz":"VARCHAR(30)",
            "manzana":"VARCHAR(100)",
            "nse":"VARCHAR(5)",
            "cod_postal":"VARCHAR(10)",
            "cod_dep":"VARCHAR(10)",
            "nom_dep":"VARCHAR(100)",
            "cod_prov":"VARCHAR(10)",
            "nom_prov":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "cod_mz": 'str:30',
                "manzana": 'str:100',
                "nse": 'str:5',
                "cod_postal": 'str:10',
                "cod_dep": 'str:10',
                "nom_dep": 'str:100',
                "cod_prov": 'str:10',
                "nom_prov": 'str:100',
                "cod_distri": 'str:10',
                "nom_distri": 'str:100',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }
        
        
    elif tabla[0:7] == 'mavvial':  
    
        print(tabla.upper())    
        
        shapefile_name = "mavvial"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "tipovia":"VARCHAR(10)",
            "nomvia":"VARCHAR(100)",
            "nomvtotal":"VARCHAR(100)",
            "generadora":"VARCHAR(50)",
            "entre_via":"VARCHAR(100)",
            "costado":"VARCHAR(1)",
            "rango_par":"VARCHAR(20)",
            "rango_imp":"VARCHAR(20)",
            "cod_postal":"VARCHAR(10)",
            "categ_vial":"VARCHAR(10)",
            "oneway":"VARCHAR(2)",
            "velocidad":"VARCHAR(3)",
            "marca_vial":"VARCHAR(10)",
            "cod_dep":"VARCHAR(10)",
            "nom_dep":"VARCHAR(100)",
            "cod_prov":"VARCHAR(10)",
            "nom_prov":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "tipovia": 'str:10',
                "nomvia": 'str:100',
                "nomvtotal": 'str:100',
                "generadora": 'str:50',
                "entre_via": 'str:100',
                "costado": 'str:1',
                "rango_par": 'str:20',
                "rango_imp": 'str:20',
                "cod_postal": 'str:10',
                "categ_vial": 'str:10',
                "oneway": 'str:2',
                "velocidad": 'str:3',
                "marca_vial": 'str:10',
                "cod_dep": 'str:10',
                "nom_dep": 'str:100',
                "cod_prov": 'str:10',
                "nom_prov": 'str:100',
                "cod_distri": 'str:10',
                "nom_distri": 'str:100',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }

        
        
    elif tabla[0:6] == 'parque':
    
        print(tabla.upper())
    
        shapefile_name = "parques_y_zonas_verdes"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "nombre":"VARCHAR(100)",
            "cod_dep":"VARCHAR(10)",
            "nom_dep":"VARCHAR(100)",
            "cod_prov":"VARCHAR(10)",
            "nom_prov":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "nombre": 'str:100',
                "cod_dep": 'str:10',
                "nom_dep": 'str:100',
                "cod_prov": 'str:10',
                "nom_prov": 'str:100',
                "cod_distri": 'str:10',
                "nom_distri": 'str:100',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }

        
    
    elif tabla[0:5] == 'placa':
    
        print(tabla.upper())
    
        shapefile_name = "placas"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "tipovia":"VARCHAR(10)",
            "nomvia":"VARCHAR(100)",
            "nomvtotal":"VARCHAR(100)",
            "generadora":"VARCHAR(50)",
            "placa":"VARCHAR(10)",
            "manzana":"VARCHAR(30)",
            "casa_lote":"VARCHAR(50)",
            "tipo_dir":"VARCHAR(20)",
            "direccion":"VARCHAR(180)",
            "cod_postal":"VARCHAR(10)",
            "id_predio":"INTEGER",
            "id_mavvial":"INTEGER",
            "cod_dep":"VARCHAR(10)",
            "nom_dep":"VARCHAR(100)",
            "cod_prov":"VARCHAR(10)",
            "nom_prov":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "observ_dat":"VARCHAR(30)",
            "observ_pos":"VARCHAR(30)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "tipovia": 'str:10',
                "nomvia": 'str:100',
                "nomvtotal": 'str:100',
                "generadora": 'str:50',
                "placa": 'str:10',
                "manzana": 'str:30',
                "casa_lote": 'str:50',
                "tipo_dir": 'str:20',
                "direccion": 'str:180',
                "cod_postal": 'str:10',
                "id_predio": 'int',
                "id_mavvial": 'int',
                "cod_dep": 'str:10',
                "nom_dep": 'str:100',
                "cod_prov": 'str:10',
                "nom_prov": 'str:100',
                "cod_distri": 'str:10',
                "nom_distri": 'str:100',
                "observ_dat": 'str:30',
                "observ_pos": 'str:30',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }


    
    elif tabla[0:6] == 'predio':   
    
        print(tabla.upper())
    
        shapefile_name = "predios"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "cod_predio":"VARCHAR(10)",
            "id_mz":"VARCHAR(30)",
            "id_malla":"VARCHAR(30)",
            "nse":"VARCHAR(5)",
            "cod_dep":"VARCHAR(10)",
            "nom_dep":"VARCHAR(100)",
            "cod_prov":"VARCHAR(10)",
            "nom_prov":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "cod_predio": 'str:10',
                "id_mz": 'str:30',
                "id_malla": 'str:30',
                "nse": 'str:5',
                "cod_dep": 'str:10',
                "nom_dep": 'str:100',
                "cod_prov": 'str:10',
                "nom_prov": 'str:100',
                "cod_distri": 'str:10',
                "nom_distri": 'str:100',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }

        
        
    elif tabla[0:9] == 'provincia':
    
        print(tabla.upper())
    
        shapefile_name = "provincias"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "cod_dep":"VARCHAR(10)",
            "nom_dep":"VARCHAR(100)",
            "cod_prov":"VARCHAR(10)",
            "nom_prov":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "cod_dep": 'str:10',
                "nom_dep": 'str:100',
                "cod_prov": 'str:10',
                "nom_prov": 'str:100',
                "cod_distri": 'str:10',
                "nom_distri": 'str:100',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }

        
    
    elif tabla[0:12] == 'urbanizacion':
    
        print(tabla.upper())
    
        shapefile_name = "urbanizaciones"  # Nombre del archivo shapefile sin extensión

        output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

        output_column_specs = {
            "id_capa":"INTEGER",
            "cod_urb":"VARCHAR(10)",
            "tipo_urb":"VARCHAR(10)",
            "nom_urb":"VARCHAR(100)",
            "cod_dep":"VARCHAR(10)",
            "nom_dep":"VARCHAR(100)",
            "cod_prov":"VARCHAR(10)",
            "nom_prov":"VARCHAR(100)",
            "cod_distri":"VARCHAR(10)",
            "nom_distri":"VARCHAR(100)",
            "marca":"VARCHAR(5)",
            "fecha":"VARCHAR(10)",
            "version":"VARCHAR(5)",
            "geom": "geometry"          
        }
        schema = {
            'geometry': 'Unknown',
            'properties': {
                "id_capa": 'int',
                "cod_urb": 'str:10',
                "tipo_urb": 'str:10',
                "nom_urb": 'str:100',
                "cod_dep": 'str:10',
                "nom_dep": 'str:100',
                "cod_prov": 'str:10',
                "nom_prov": 'str:100',
                "cod_distri": 'str:10',
                "nom_distri": 'str:100',
                "marca": 'str:5',
                "fecha": 'str:10',
                "version": 'str:5'
            }
        }
    else:
        print("No existe Estructura Para Exportar la Capa")
        return   
    
    try:

        with engine.connect() as connection:
            # Preparar la consulta
            column_casts = ", ".join([f"CAST({col} AS {spec}) AS {col}" for col, spec in output_column_specs.items()])
            #print(column_casts)
            
            query = f"SELECT {column_casts} FROM {tabla};"
            #print(query)

            # Cargar los datos como un GeoDataFrame
            gdf = gpd.read_postgis(query, connection, geom_col="geom")
            
            # Exportar los datos como un Shapefile
            gdf.to_file(output_file,engine="fiona", driver="ESRI Shapefile", schema=schema)
            print(f"Shapefile exportado correctamente a {output_file}")

    except Exception as e:
        print(f"Error: {e}")


def Chile_QueryExpGdb(engine,lista,carpeta_final):

    print(lista)

    for tabla in lista:
    
        if tabla[0:8] == 'distrito':
            #print('si entre')
            print(tabla.upper())

            shapefile_name = "distritos"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "cod_dep":"VARCHAR(10)",
                "nom_dep":"VARCHAR(100)",
                "cod_prov":"VARCHAR(10)",
                "nom_prov":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "observ":"VARCHAR(30)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "cod_dep": 'str:10',
                    "nom_dep": 'str:100',
                    "cod_prov": 'str:10',
                    "nom_prov": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "observ": 'str:30',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }
            
            exportar = True
        
        elif tabla[0:12] == 'departamento':
            print(tabla.upper())    
            shapefile_name = "departamentos"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "cod_dep":"VARCHAR(10)",
                "nom_dep":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "cod_dep": 'str:10',
                    "nom_dep": 'str:100',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }
                
            exportar = True
            
        elif tabla[0:11] == 'hidrografia':
            print(tabla.upper())
            
            shapefile_name = "hidrografia"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "nombre":"VARCHAR(100)",
                "cod_dep":"VARCHAR(10)",
                "nom_dep":"VARCHAR(100)",
                "cod_prov":"VARCHAR(10)",
                "nom_prov":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "nombre": 'str:100',
                    "cod_dep": 'str:10',
                    "nom_dep": 'str:100',
                    "cod_prov": 'str:10',
                    "nom_prov": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }

            exportar = True
                
        elif tabla[0:7] == 'manzana':
            print(tabla.upper())
            
            shapefile_name = "manzanas"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "cod_mz":"VARCHAR(30)",
                "manzana":"VARCHAR(100)",
                "nse":"VARCHAR(5)",
                "cod_postal":"VARCHAR(10)",
                "cod_dep":"VARCHAR(10)",
                "nom_dep":"VARCHAR(100)",
                "cod_prov":"VARCHAR(10)",
                "nom_prov":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "cod_mz": 'str:30',
                    "manzana": 'str:100',
                    "nse": 'str:5',
                    "cod_postal": 'str:10',
                    "cod_dep": 'str:10',
                    "nom_dep": 'str:100',
                    "cod_prov": 'str:10',
                    "nom_prov": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }
            
            exportar = True
            
        elif tabla[0:7] == 'mavvial':  
        
            print(tabla.upper())    
            
            shapefile_name = "mavvial"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "tipovia":"VARCHAR(10)",
                "nomvia":"VARCHAR(100)",
                "nomvtotal":"VARCHAR(100)",
                "generadora":"VARCHAR(50)",
                "entre_via":"VARCHAR(100)",
                "costado":"VARCHAR(1)",
                "rango_par":"VARCHAR(20)",
                "rango_imp":"VARCHAR(20)",
                "cod_postal":"VARCHAR(10)",
                "categ_vial":"VARCHAR(10)",
                "oneway":"VARCHAR(2)",
                "velocidad":"VARCHAR(3)",
                "marca_vial":"VARCHAR(10)",
                "cod_dep":"VARCHAR(10)",
                "nom_dep":"VARCHAR(100)",
                "cod_prov":"VARCHAR(10)",
                "nom_prov":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "tipovia": 'str:10',
                    "nomvia": 'str:100',
                    "nomvtotal": 'str:100',
                    "generadora": 'str:50',
                    "entre_via": 'str:100',
                    "costado": 'str:1',
                    "rango_par": 'str:20',
                    "rango_imp": 'str:20',
                    "cod_postal": 'str:10',
                    "categ_vial": 'str:10',
                    "oneway": 'str:2',
                    "velocidad": 'str:3',
                    "marca_vial": 'str:10',
                    "cod_dep": 'str:10',
                    "nom_dep": 'str:100',
                    "cod_prov": 'str:10',
                    "nom_prov": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }

            exportar = True
            
        elif tabla[0:6] == 'parque':
        
            print(tabla.upper())
        
            shapefile_name = "parques_y_zonas_verdes"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "nombre":"VARCHAR(100)",
                "cod_dep":"VARCHAR(10)",
                "nom_dep":"VARCHAR(100)",
                "cod_prov":"VARCHAR(10)",
                "nom_prov":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "nombre": 'str:100',
                    "cod_dep": 'str:10',
                    "nom_dep": 'str:100',
                    "cod_prov": 'str:10',
                    "nom_prov": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }

            exportar = True
        
        elif tabla[0:5] == 'placa':
        
            print(tabla.upper())
        
            shapefile_name = "placas"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "tipovia":"VARCHAR(10)",
                "nomvia":"VARCHAR(100)",
                "nomvtotal":"VARCHAR(100)",
                "generadora":"VARCHAR(50)",
                "placa":"VARCHAR(10)",
                #"cod_urb":"VARCHAR(10)",
                #"tipo_urb":"VARCHAR(10)",
                #"nom_urb":"VARCHAR(100)",
                "manzana":"VARCHAR(30)",
                "casa_lote":"VARCHAR(50)",
                "tipo_dir":"VARCHAR(20)",
                "direccion":"VARCHAR(180)",
                "cod_postal":"VARCHAR(10)",
                "id_predio":"INTEGER",
                "id_mavvial":"INTEGER",
                "cod_dep":"VARCHAR(10)",
                "nom_dep":"VARCHAR(100)",
                "cod_prov":"VARCHAR(10)",
                "nom_prov":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "observ_dat":"VARCHAR(30)",
                "observ_pos":"VARCHAR(30)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "tipovia": 'str:10',
                    "nomvia": 'str:100',
                    "nomvtotal": 'str:100',
                    "generadora": 'str:50',
                    "placa": 'str:10',
                    "manzana": 'str:30',
                    "casa_lote": 'str:50',
                    "tipo_dir": 'str:20',
                    "direccion": 'str:180',
                    "cod_postal": 'str:10',
                    "id_predio": 'int',
                    "id_mavvial": 'int',
                    "cod_dep": 'str:10',
                    "nom_dep": 'str:100',
                    "cod_prov": 'str:10',
                    "nom_prov": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "observ_dat": 'str:30',
                    "observ_pos": 'str:30',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }

            exportar = True
        
        elif tabla[0:6] == 'predio':   
        
            print(tabla.upper())
        
            shapefile_name = "predios"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "cod_predio":"VARCHAR(10)",
                "id_mz":"VARCHAR(30)",
                "id_malla":"VARCHAR(30)",
                "nse":"VARCHAR(5)",
                "cod_dep":"VARCHAR(10)",
                "nom_dep":"VARCHAR(100)",
                "cod_prov":"VARCHAR(10)",
                "nom_prov":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "cod_predio": 'str:10',
                    "id_mz": 'str:30',
                    "id_malla": 'str:30',
                    "nse": 'str:5',
                    "cod_dep": 'str:10',
                    "nom_dep": 'str:100',
                    "cod_prov": 'str:10',
                    "nom_prov": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }

            exportar = True
            
        elif tabla[0:9] == 'provincia':
        
            print(tabla.upper())
        
            shapefile_name = "provincias"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "cod_dep":"VARCHAR(10)",
                "nom_dep":"VARCHAR(100)",
                "cod_prov":"VARCHAR(10)",
                "nom_prov":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "cod_dep": 'str:10',
                    "nom_dep": 'str:100',
                    "cod_prov": 'str:10',
                    "nom_prov": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }

            exportar = True
        
        elif tabla[0:12] == 'urbanizacion':
        
            print(tabla.upper())
        
            shapefile_name = "urbanizaciones"  # Nombre del archivo shapefile sin extensión

            output_file = os.path.join(carpeta_final, f"{shapefile_name}.shp")

            output_column_specs = {
                "id_capa":"INTEGER",
                "cod_urb":"VARCHAR(10)",
                "tipo_urb":"VARCHAR(10)",
                "nom_urb":"VARCHAR(100)",
                "cod_dep":"VARCHAR(10)",
                "nom_dep":"VARCHAR(100)",
                "cod_prov":"VARCHAR(10)",
                "nom_prov":"VARCHAR(100)",
                "cod_distri":"VARCHAR(10)",
                "nom_distri":"VARCHAR(100)",
                "marca":"VARCHAR(5)",
                "fecha":"VARCHAR(10)",
                "version":"VARCHAR(5)",
                "geom": "geometry"          
            }
            schema = {
                'geometry': 'Unknown',
                'properties': {
                    "id_capa": 'int',
                    "cod_urb": 'str:10',
                    "tipo_urb": 'str:10',
                    "nom_urb": 'str:100',
                    "cod_dep": 'str:10',
                    "nom_dep": 'str:100',
                    "cod_prov": 'str:10',
                    "nom_prov": 'str:100',
                    "cod_distri": 'str:10',
                    "nom_distri": 'str:100',
                    "marca": 'str:5',
                    "fecha": 'str:10',
                    "version": 'str:5'
                }
            }
            
            exportar = True
        else:
            print("No existe Estructura Para Exportar la Capa")
      
        if exportar:
            try:

                with engine.connect() as connection:
                    # Preparar la consulta
                    column_casts = ", ".join([f"CAST({col} AS {spec}) AS {col}" for col, spec in output_column_specs.items()])
                    #print(column_casts)
                    
                    query = f"SELECT {column_casts} FROM {tabla};"
                    #print(query)

                    # Cargar los datos como un GeoDataFrame
                    gdf = gpd.read_postgis(query, connection, geom_col="geom")

                    # Exportar los datos como un Shapefile
                    gdf.to_file(output_file,engine="fiona", driver="ESRI Shapefile", schema=schema)
                    print(f"Shapefile exportado correctamente a {output_file}")

            except Exception as e:
                print(f"Error: {e}")