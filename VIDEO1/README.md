# Scrapping de las negociaciones de la Bolsa de Madrid

Codigo fuente del contenido del primer video distinado a los miembros de la comunidad Pynacle

Este código es para solamente fines educativos, si quierees usar los datos para otros fines debes pedir autorización  BME Market Data.

La información facilitada en las distintas páginas webs del Grupo BME está destinada, exclusivamente, al uso interno de la misma. 
Para llevar a cabo cualquier otro uso con fines comerciales y/o que implique la redifusión a terceros de dicha información de forma no gratuita es necesario contar con la autorización expresa previa de BME Market Data (marketdata@grupobme.es).

*VIDEO 1*

En ete video se ha simplificado al maximo la obtención de datos de las negociaciones de la Bolsa de Madrid.

Las empresas a consultar las almacenamos en un fichero json i los resultados se guardan en formato Excel.

*Parte 1*
En la primera parte se obtienen los datos de las negociaciones de la Bolsa de Madrid, tal qual

*Parte 2*
En la segunda parte se intenta ir un paso más allà i agregar las operaciones obtenidas.
Se parte de la suposición que todas las operaciones realitzadas en el mismo segudo se pueden agregar en una sola operación.
Si la operación agregada hace subir el precio anterior a la operación entendemos que se trata de una compra, si lo hace bajar entendemos que se trata de una venta
Si se mantiene el precio, imputaremos una compra o una venta en función de la última operación realizada.

Si es de interés en un proximo video, crearemos una base de datos donde almacenaremos tanto las empresas como los resultados obtenidos, de manera que podremos consultar mediante sentencias SQL los datos obtenidos y obtener graficas





