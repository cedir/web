from decimal import Decimal


def run_sanity():
    """
    Toma la columna importe y la suma. Muestra el resultado para comparar con la Factura.
    """

    with open('/home/walter/Documents/presentacion_OSDE BINARIO_2019-01-15.txt') as fp:

        total = 0
        for line in fp:
            monto = line[75:91]
            integer_part = monto[:13]
            decimal_part = monto[13:15]
            if not monto:
                print('X')
                continue
            monto = Decimal('{}.{}'.format(integer_part, decimal_part))
            total +=monto

        print(total)


if __name__ == '__main__':
    run_sanity()
