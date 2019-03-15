from decimal import Decimal, ROUND_UP

# TODO:
# - Ver en que orden aparecen los estudios en el azul, y ordenarlos igual aca
# - Escribir test?
# - arancel_anestesia y diferencia paciente se suman al total del estudio o no? y en OSDE?

class AmrRowBase(object):
    def __init__(self, estudio, comprobante, *args, **kwargs):
        """
        Codigo de Prestador	1	6
        Codigo de Convenio	7	11
        Numero de Factura	12	19
        Numero de Rendicion	20	26
        Codigo de Afiliado	27	41
        Nombre de Afiliado	42	71
        Tipo Documento	72	72
        Numero de documento	73	80
        Numero de Bono	81	87
        Fecha	88	95
        Codigo de Nomenclador Prestacional	96	102
        Tipo de Nomenclador Prestacional	103	103
        Nombre de Nomenclador Prestacional	104	133
        Cantidad	134	138
        Matricula del Efector	139	144
        Nombre del Efector	145	174
        Honorarios	175	187
        Derechos	188	200
        Tipo de honorario	201	201
        Porcentaje honorario	202	204
        Porcentaje derechos	205	207
        Urgencia	208	208
        Matricula del Prescriptor	209	214
        Nombre del Prescriptor	215	244
        Codigo de Autorizacion	245	255
        Medicamentos y Descartables	256	268
        """
        importe = Decimal(estudio.importe_estudio).quantize(Decimal('.01'), ROUND_UP)
        importe_pension = Decimal(estudio.pension).quantize(Decimal('.01'), ROUND_UP)
        importe_medicacion = Decimal(estudio.importe_medicacion).quantize(Decimal('.01'), ROUND_UP)

        self.codigo_de_prestador = u'{:<6}'.format('')
        self.codigo_de_convenio = u'{:<5}'.format('')
        self.numero_de_factura = u'{0:08}'.format(comprobante.numero)
        self.numero_de_rendicion = u'{:<7}'.format('')
        self.codigo_de_afiliado = u'{:<15}'.format(self.format_nro_afiliado(estudio.paciente))
        self.nombre_de_afiliado = u'{:<30}'.format(unicode(estudio.paciente)[:30])
        self.tipo_documento = u'0'
        self.numero_de_documento = u'{:<8}'.format(unicode(estudio.paciente.dni)[:8])
        self.numero_de_bono = u'{:<8}'.format(estudio.nro_de_orden[:8])  # nro de orden
        self.fecha = u'{}'.format(estudio.fecha.strftime('%Y%m%d'))  # AAAAMMDD
        self.codigo_de_nomenclador_prestacional = '{0:<7}'.format(estudio.practica.codigoMedico[:7])
        self.tipo_de_nomenclador_prestacional = u'M'
        self.nombre_de_nomenclador_prestacional = u'{:<30}'.format(unicode(estudio.practica)[:30])
        self.cantidad = u'00001'
        self.matricula_del_efector = '{0:06}'.format(self.format_nro_matricula(estudio.medico))
        self.nombre_del_efector = u'{:<30}'.format(unicode(estudio.medico)[:30])
        self.honorarios = '0{0:013}'.format(importe).replace('.', '')
        self.derechos = '0{0:013}'.format(importe_pension).replace('.', '')
        self.tipo_de_honorario = u'0'
        self.porcentaje_honorario = u'100'
        self.porcentaje_derechos = u'100'
        self.urgencia = u'N'  # S=Si, N=No
        self.matricula_del_prescriptor = '{0:06}'.format(self.format_nro_matricula(estudio.medico_solicitante))
        self.nombre_del_prescriptor = u'{:<30}'.format(unicode(estudio.medico_solicitante)[:30])
        self.codigo_de_autorizacion = u'{:<11}'.format('')  # no lo tenemos
        self.medicamentos_y_descartables = '0{0:013}'.format(importe_medicacion).replace('.', '')

    def get_row(self):
        return self.codigo_de_prestador + self.codigo_de_convenio + self.numero_de_factura + self.numero_de_rendicion +\
               self.codigo_de_afiliado + self.nombre_de_afiliado + self.tipo_documento + self.numero_de_documento +\
               self.numero_de_bono + self.fecha + self.codigo_de_nomenclador_prestacional +\
               self.tipo_de_nomenclador_prestacional + self.nombre_de_nomenclador_prestacional + self.cantidad +\
               self.matricula_del_efector + self.nombre_del_efector + self.honorarios + self.derechos +\
               self.tipo_de_honorario + self.porcentaje_honorario + self.porcentaje_derechos + self.urgencia + \
               self.matricula_del_prescriptor + self.nombre_del_prescriptor + self.codigo_de_autorizacion + \
               self.medicamentos_y_descartables

    def format_nro_afiliado(self, paciente):
        nro_afiliado = paciente.nroAfiliado.replace(' ', '')
        nro_afiliado = nro_afiliado.replace('-', '')
        nro_afiliado = nro_afiliado[:15]  # corto en 15
        return nro_afiliado

    def format_nro_matricula(self, medico):
        nro_matricula = medico.matricula
        try:
            nro_matricula = nro_matricula.split(u' ')[0]
            nro_matricula = int(nro_matricula[:6])
            return nro_matricula
        except ValueError:
            raise ValueError("Error con la matricula del medico {}({}) - Matricula {}".format(medico.apellido, medico.id,
                                                                                              nro_matricula))


class AmrRowEstudio(AmrRowBase):
    def __init__(self, estudio, *args, **kwargs):
        super(AmrRowEstudio, self).__init__(estudio, *args, **kwargs)
