from flask import Flask
from flask import render_template, request, redirect
from flaskext.mysql import MySQL
from datetime import datetime
import os

app= Flask(__name__)
mysql= MySQL()

app.config['MYSQL_DATABASE_HOST']= 'localhost'
app.config['MYSQL_DATABASE_USER']= 'root'
app.config['MYSQL_DATABASE_PASSWORD']= 'root'
app.config['MYSQL_DATABASE_DB']= 'empleados'

UPLOADS = os.path.join('uploads')
app.config['UPLOADS'] = UPLOADS # guardamos la ruta como un valor en la app

mysql.init_app(app)


@app.route('/') # define una ruta de acceso
def index():
    conn=mysql.connect()
    cursor = conn.cursor()

    sql= "SELECT * FROM `empleados`.`empleados`;"
    cursor.execute(sql)
    
    empleados = cursor.fetchall()

    conn.commit()

    return render_template('empleados/index.html', empleados=empleados)

@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre'] # lo recibe del form
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto'] # lo recibe como archivo, un stream de datos

    now = datetime.now()
    print(now)
    tiempo = now.strftime("%Y%H%M%S")
    print(tiempo)

    if _foto.filename != '':
        nuevoNombreFoto = tiempo + '_' + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)

    
    sql= "INSERT INTO  `empleados`.`empleados` (nombre, correo, foto) VALUES (%s,%s,%s);"
    datos= (_nombre,_correo,nuevoNombreFoto)

    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/')


@app.route('/modify/<int:id>')
def modify(id):
    sql = f'SELECT * FROM `empleados`.`empleados` WHERE id={id}' # puedo usar f'{}' o %s. lo q me sea mas comodo
    conn = mysql.connect()
    cursor= conn.cursor()
    cursor.execute(sql)
    empleado= cursor.fetchone()
    conn.commit()

    return render_template('empleados/edit.html', empleado = empleado)

@app.route('/update', methods=['POST'])
def update():
    _nombre= request.form['txtNombre']
    _correo= request.form['txtCorreo']
    _foto= request.files['txtFoto']
    id= request.form['txtId']

    datos = (_nombre, _correo, id)

    conn= mysql.connect()
    cursor= conn.cursor()

    if _foto.filename != '':
        now = datetime.now()
        tiempo= now.strftime("%Y%H%M%S")
        nuevoNombreFoto = tiempo + '_' + _foto.filename
        _foto.save("uploads/" + nuevoNombreFoto)
    
    sql= f'SELECT foto FROM `empleados`.`empleados` WHERE id={id}'
    cursor.execute(sql)

    nombreFoto = cursor.fetchone()[0] # esto esta muy feo

    os.remove(os.path.join(app.config['UPLOADS'], nombreFoto))

    conn= mysql.connect()
    cursor=conn.cursor()

    sql= f'UPDATE `empleados`.`empleados` SET nombre={_nombre}, correo={_correo} WHERE id={id}'
    cursor.execute(sql)
    conn.commit()


@app.route('/delete/<int:id>') # lo que está entre <> es un parámetro.
def delete(id):
    # sql = "DELETE FROM `empleados`.`empleados` WHERE id=%s"
    sql = f'DELETE FROM `empleados`.`empleados` WHERE id={id}'
    conn = mysql.connect()
    cursor = conn.cursor()
    # cursor.execute(sql,id)
    cursor.execute(sql)
    conn.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)