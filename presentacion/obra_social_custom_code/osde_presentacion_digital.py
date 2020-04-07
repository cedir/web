from decimal import Decimal, ROUND_UP


class OsdeRowBase(object):
    def __init__(self, estudio, *args, **kwargs):
        self.nro_prestador_cedir = '051861'
        self.nro_afiliado = self.format_nro_afiliado(estudio.paciente)
        self.codigo_medico_osde = None
        self.tipo_prestacion = '1'  # ambulatorio
        self.cantidad = '001'
        self.fecha = estudio.fecha.strftime('%d%m%y')  # DDMMAA
        self.dlegacion_emisora = '00'
        self.nro_de_orden = '000000'
        self.tipo_orden = '0'
        self.importe = None
        self.letra_espec_efector = self.letra_espec_prescriptor = 'M'  #  Es la letra que identifica la especialidad del profesional (M= medico, B= bioquimico, etc)
        self.nro_matricula_prescriptor = self.format_nro_matricula(estudio.medico_solicitante)
        self.provincia_matricula = 'S'  # santa Fe
        self.nro_matricula_efector = self.format_nro_matricula(estudio.medico)
        self.transacion = '{0:<6}'.format(estudio.nro_de_orden[:6])
        self.prestador_prescriptor = '000000'

    def get_row_osde(self):
        """
        espacios 0 1
        N Prestador	2	7
        N Afiliado	11	21
        Codigo Prestacion	25	30
        Tipo de Prestacion	31	31
        Cantidad de prestacion	43	45
        Fecha 	49	54
        Dlegacion Emisora	58	59
        N Orden	63	68
        Tipo de Orden	72	72
        Importe	76	90
        Letra Espec. Prescriptor	94	94
        N Matricula - Prescriptor	98	107
        Provincia de Matricula	111	111
        Letra Espec. Efector	115	115
        N Matricula - Efector	119	128
        Provincia de Matricula	132	132
        Transacion	136	141
        Prestador Prescriptor	145	150
        """
        filas_1 = '{:<1}{}{:<3}{}{:<3}{}{}{:<11}{}{:<3}{}'.format('', self.nro_prestador_cedir, '', self.nro_afiliado, '',
                                                                  self.codigo_medico_osde, self.tipo_prestacion, '',
                                                                  self.cantidad, '', self.fecha)
        filas_2 = '{:<3}{}{:<3}{}{:<3}{}{:<3}{}'.format('', self.dlegacion_emisora, '', self.nro_de_orden, '',
                                                        self.tipo_orden, '', self.importe)
        filas_medico_solicitante = '{:<3}{}{:<3}{}{:<3}{}'.format('', self.letra_espec_prescriptor, '',
                                                                  self.nro_matricula_prescriptor, '', self.provincia_matricula)
        filas_medico_actuante = '{:<3}{}{:<3}{}{:<3}{}'.format('', self.letra_espec_efector, '', self.nro_matricula_efector,
                                                               '', self.provincia_matricula)
        filas_final = '{:<3}{}{:<3}{}'.format('', self.transacion, '', self.prestador_prescriptor)

        return filas_1 + filas_2 + filas_medico_solicitante + filas_medico_actuante + filas_final

    def format_nro_afiliado(self, paciente):
        nro_afiliado = paciente.nroAfiliado.replace(' ', '')
        nro_afiliado = nro_afiliado.replace('-', '')
        nro_afiliado = nro_afiliado[:11]
        try:
            assert len(nro_afiliado) == 11
            return nro_afiliado
        except AssertionError:
            raise Exception('Nro de Afiliado debe ser 11 caracteres numericos para {}({}) - Nro Afiliado: {}'.format(paciente, paciente.id, nro_afiliado))

    def format_nro_matricula(self, medico):
        nro_matricula = medico.matricula if medico.facturar_osde_en_nombre_de_medico == None else medico.facturar_osde_en_nombre_de_medico.matricula
        try:
            nro_matricula = nro_matricula.split(u' ')[0]
            nro_matricula = int(nro_matricula)
            return '{0:010}'.format(nro_matricula)
        except ValueError:
            raise ValueError("Error con la matricula del medico {}({}) - Matricula {}".format(medico.apellido, medico.id, nro_matricula))


class OsdeRowEstudio(OsdeRowBase):
    def __init__(self, estudio, *args, **kwargs):
        super(OsdeRowEstudio, self).__init__(estudio, *args, **kwargs)
        self.codigo_medico_osde = '{0:<6}'.format(estudio.practica.codigo_medico_osde[:6])
        importe = Decimal(estudio.importe_estudio).quantize(Decimal('.01'), ROUND_UP)
        self.importe = '{0:015}'.format(importe)
        self.importe = '0{}'.format(self.importe.replace('.', ''))  # remuevo punto decimal, y agrego cero para complementar


class OsdeRowMedicacion(OsdeRowBase):
    def __init__(self, estudio, *args, **kwargs):
        super(OsdeRowMedicacion, self).__init__(estudio, *args, **kwargs)
        self.codigo_medico_osde = '925525'
        self.importe = '{0:015}'.format(estudio.get_total_medicacion())
        self.importe = '0{}'.format(self.importe.replace('.', ''))  # remuevo punto decimal, y agrego cero para complementar


class OsdeRowPension(OsdeRowBase):
    def __init__(self, estudio, *args, **kwargs):
        super(OsdeRowPension, self).__init__(estudio, *args, **kwargs)
        self.codigo_medico_osde = '430185'
        importe = Decimal(estudio.pension).quantize(Decimal('.01'), ROUND_UP)
        self.importe = '{0:015}'.format(importe)
        self.importe = '0{}'.format(self.importe.replace('.', ''))  # remuevo punto decimal, y agrego cero para complementar


class OsdeRowMaterialEspecifico(OsdeRowBase):
    def __init__(self, estudio, material_especifico, *args, **kwargs):
        super(OsdeRowMaterialEspecifico, self).__init__(estudio, *args, **kwargs)
        self.codigo_medico_osde = '{0:<6}'.format(material_especifico.medicamento.codigo_osde[:6])
        importe = Decimal(material_especifico.importe).quantize(Decimal('.01'), ROUND_UP)
        self.importe = '{0:015}'.format(importe)
        self.importe = '0{}'.format(self.importe.replace('.', ''))  # remuevo punto decimal, y agrego cero para complementar
