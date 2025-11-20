"""
Script para importar productos desde recetario_flores.csv
Crea/actualiza flores, contenedores y productos con sus recetas
"""

import sys
import os
import csv
from datetime import datetime

# Añadir el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from extensions import db
from models.inventario import Flor, Contenedor
from models.producto import Producto, RecetaProducto
from app import app

# Mapeo de nombres de columnas CSV a nombres de insumos
COLUMNAS_FLORES = {
    'PEONIAS_HORTENSIAS': 'Peonías/Hortensias',
    'ROSAS': 'Rosas',
    'GERBERAS': 'Gerberas',
    'ALSTROMERIAS': 'Alstromerias',
    'PERROS_DIGITALIS': 'Perros/Digitalis',
    'BLUPERIUM': 'Bluperium',
    'LISIANTHUS': 'Lisianthus',
    'GREENBALL': 'Greenball',
    'TRAQUELIUM': 'Traquelium',
    'SPIDER': 'Spider',
    'CREMON_MABLE': 'Cremón/Mable',
    'HYPERICUM': 'Hypericum',
    'HELLEBORUS': 'Helleborus',
    'ESCABIOSA': 'Escabiosa',
    'RANUNCULOS': 'Ranúnculos',
    'VERÓNICAS': 'Verónicas',
    'PROTEAS': 'Proteas',
    'LENTEJAS': 'Lentejas',
    'LILIUMS': 'Liliums',
    'ANÉMONAS': 'Anémonas',
    'HIEDRA': 'Hiedra',
    'MINI_ROSA': 'Mini Rosa',
    'MINI_GERBERA': 'Mini Gerbera',
    'FRESIA': 'Fresia',
    'IRIS': 'Iris',
    'DELPHINIUM': 'Delphinium',
    'AGAPANTOS': 'Agapantos',
    'REPOLLOS': 'Repollos',
    'CARDO_AZUL': 'Cardo Azul',
    'CLAVEL_MINI': 'Clavel Mini',
    'ERINGIOS': 'Eringios',
    'PAJARITOS': 'Pajaritos',
    'CICUTA_LIMONIUM': 'Cicuta/Limonium',
    'ACUARANTUS': 'Acuarantus'
}

def limpiar_valor(valor):
    """Limpia y convierte valores del CSV"""
    if not valor or valor.strip() == '':
        return None
    valor = valor.strip()

    # Intentar convertir a número
    try:
        # Si tiene /, tomar el primer número (ej: "1/2" -> 0.5, "3-4" -> 3)
        if '/' in valor:
            partes = valor.split('/')
            return float(partes[0]) / float(partes[1])
        elif '-' in valor and valor[0].isdigit():
            # Rango como "3-4", tomar el promedio
            partes = valor.split('-')
            return (float(partes[0]) + float(partes[1])) / 2
        else:
            return float(valor)
    except:
        # Si no es número, devolver como texto
        return valor

def obtener_o_crear_flor(nombre, flores_existentes):
    """Obtiene una flor existente o crea una nueva"""
    # Buscar en flores existentes
    flor = next((f for f in flores_existentes if f.nombre and f.nombre.lower() == nombre.lower()), None)

    if not flor:
        # Generar ID
        max_id = db.session.query(db.func.max(Flor.id)).scalar()
        if max_id:
            try:
                numero = int(max_id.split('_')[1]) + 1
            except:
                numero = 1
        else:
            numero = 1
        flor_id = f"FLO_{numero:03d}"

        # Crear nueva flor con INSERT directo
        from sqlalchemy import text
        db.session.execute(
            text("INSERT INTO flores (id, tipo, nombre, cantidad_stock, cantidad_en_uso) VALUES (:id, :tipo, :nombre, 0, 0)"),
            {'id': flor_id, 'tipo': nombre, 'nombre': nombre}
        )
        db.session.flush()
        flor = Flor.query.get(flor_id)
        print(f"  ✅ Flor creada: {nombre} (ID: {flor.id})")
        flores_existentes.append(flor)

    return flor

def obtener_o_crear_contenedor(nombre, contenedores_existentes):
    """Obtiene un contenedor existente o crea uno nuevo"""
    # Buscar en contenedores existentes
    contenedor = next((c for c in contenedores_existentes if c.nombre and c.nombre.lower() == nombre.lower()), None)

    if not contenedor:
        # Generar ID
        max_id = db.session.query(db.func.max(Contenedor.id)).scalar()
        if max_id:
            try:
                numero = int(max_id.split('_')[1]) + 1
            except:
                numero = 1
        else:
            numero = 1
        cont_id = f"CON_{numero:03d}"

        # Crear nuevo contenedor con INSERT directo
        from sqlalchemy import text
        db.session.execute(
            text("INSERT INTO contenedores (id, nombre, cantidad_stock, cantidad_en_uso, cantidad_en_evento, stock) VALUES (:id, :nombre, 0, 0, 0, 0)"),
            {'id': cont_id, 'nombre': nombre}
        )
        db.session.flush()
        contenedor = Contenedor.query.get(cont_id)
        print(f"  ✅ Contenedor creado: {nombre} (ID: {contenedor.id})")
        contenedores_existentes.append(contenedor)

    return contenedor

def generar_id_producto():
    """Genera un ID único para producto"""
    max_producto = db.session.query(db.func.max(Producto.id)).scalar()
    if max_producto:
        # Extraer número del ID (ej: "PROD_001" -> 1)
        try:
            numero = int(max_producto.split('_')[1]) + 1
        except:
            numero = 1
    else:
        numero = 1
    return f"PROD_{numero:03d}"

def importar_recetario(csv_path):
    """Importa productos desde el CSV del recetario"""

    with app.app_context():
        print("="*80)
        print("🌸 IMPORTACIÓN DE RECETARIO DE PRODUCTOS")
        print("="*80)

        # Cargar flores y contenedores existentes
        flores_existentes = Flor.query.all()
        contenedores_existentes = Contenedor.query.all()

        print(f"\n📊 Estado actual:")
        print(f"   Flores en BD: {len(flores_existentes)}")
        print(f"   Contenedores en BD: {len(contenedores_existentes)}")

        # Leer CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            productos_creados = 0
            productos_actualizados = 0

            for row in reader:
                nombre = row.get('NOMBRE', '').strip()
                if not nombre:
                    continue

                print(f"\n🌸 Procesando: {nombre}")

                # Verificar si el producto ya existe
                producto = Producto.query.filter_by(nombre=nombre).first()

                if producto:
                    print(f"   ⚠️  Producto existe, actualizando...")
                    # Limpiar recetas existentes
                    RecetaProducto.query.filter_by(producto_id=producto.id).delete()
                    productos_actualizados += 1
                else:
                    # Crear nuevo producto
                    altura = limpiar_valor(row.get('ALTURA'))
                    ancho = limpiar_valor(row.get('ANCHO'))
                    descripcion_extra = f"Altura: {altura}cm, Ancho: {ancho}cm" if altura and ancho else ""

                    producto_id = generar_id_producto()
                    precio_venta = limpiar_valor(row.get('PRECIO_VENTA', 0)) or 0

                    # Crear producto con INSERT directo para incluir todos los campos
                    from sqlalchemy import text
                    db.session.execute(
                        text("""
                            INSERT INTO productos
                            (id, nombre, descripcion, tipo_arreglo, precio_venta, activo, fecha_creacion, categoria, precio)
                            VALUES
                            (:id, :nombre, :descripcion, :tipo_arreglo, :precio_venta, :activo, :fecha_creacion, :categoria, :precio)
                        """),
                        {
                            'id': producto_id,
                            'nombre': nombre,
                            'descripcion': f'Producto importado desde recetario. {descripcion_extra}',
                            'tipo_arreglo': 'Arreglo Floral',
                            'precio_venta': precio_venta,
                            'activo': True,
                            'fecha_creacion': datetime.now(),
                            'categoria': 'Arreglos Florales',
                            'precio': precio_venta
                        }
                    )
                    db.session.flush()
                    # Obtener el producto recién creado
                    producto = Producto.query.get(producto_id)
                    db.session.add(producto)
                    db.session.flush()
                    print(f"   ✅ Producto creado (ID: {producto.id})")
                    productos_creados += 1

                # Procesar contenedor/base
                base = row.get('BASE', '').strip()
                tipo_base = row.get('TIPO_BASE', '').strip()

                if base:
                    contenedor = obtener_o_crear_contenedor(base, contenedores_existentes)
                    # Agregar a receta
                    receta = RecetaProducto(
                        producto_id=producto.id,
                        insumo_tipo='Contenedor',
                        insumo_id=contenedor.id,
                        cantidad=1,
                        unidad='unidades'
                    )
                    db.session.add(receta)
                    print(f"     → Base: {base}")

                # Procesar oasis si existe
                oasis = limpiar_valor(row.get('OASIS'))
                tipo_oasis = row.get('TIPO_OASIS', '').strip()

                if oasis and tipo_oasis and tipo_oasis.upper() != 'NO':
                    nombre_oasis = f"Oasis {tipo_oasis}"
                    contenedor_oasis = obtener_o_crear_contenedor(nombre_oasis, contenedores_existentes)
                    cantidad_oasis = oasis if isinstance(oasis, (int, float)) else 1

                    receta = RecetaProducto(
                        producto_id=producto.id,
                        insumo_tipo='Contenedor',
                        insumo_id=contenedor_oasis.id,
                        cantidad=cantidad_oasis,
                        unidad='unidades'
                    )
                    db.session.add(receta)
                    print(f"     → Oasis: {nombre_oasis} x{cantidad_oasis}")

                # Procesar flores
                flores_en_receta = 0
                for col_csv, nombre_flor in COLUMNAS_FLORES.items():
                    cantidad = limpiar_valor(row.get(col_csv))

                    if cantidad and isinstance(cantidad, (int, float)) and cantidad > 0:
                        flor = obtener_o_crear_flor(nombre_flor, flores_existentes)

                        receta = RecetaProducto(
                            producto_id=producto.id,
                            insumo_tipo='Flor',
                            insumo_id=flor.id,
                            cantidad=cantidad,
                            unidad='tallos'
                        )
                        db.session.add(receta)
                        flores_en_receta += 1
                        print(f"     → {nombre_flor}: {cantidad} tallos")

                print(f"   ✅ Receta: {flores_en_receta} tipos de flores")

        # Commit final
        db.session.commit()

        print("\n" + "="*80)
        print("✅ IMPORTACIÓN COMPLETADA")
        print("="*80)
        print(f"   Productos creados: {productos_creados}")
        print(f"   Productos actualizados: {productos_actualizados}")
        print(f"   Total flores en BD: {Flor.query.count()}")
        print(f"   Total contenedores en BD: {Contenedor.query.count()}")
        print(f"   Total productos en BD: {Producto.query.count()}")
        print("="*80)

if __name__ == '__main__':
    csv_path = '/Users/juliettegramatges/Las-Lira/recetario_flores.csv'

    if not os.path.exists(csv_path):
        print(f"❌ Error: No se encuentra el archivo {csv_path}")
        sys.exit(1)

    importar_recetario(csv_path)
