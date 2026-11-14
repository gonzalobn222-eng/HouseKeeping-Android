"""HouseKeeping Android - prototipo nativo Kivy offline."""
import io
import json
import os
from datetime import date
from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image as KivyImage
from PIL import Image as PILImage, ImageOps
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as ExcelImage

ROOT = Path(__file__).resolve().parent
QUESTIONS = json.loads((ROOT / 'assets' / 'preguntas.json').read_text(encoding='utf-8'))
TEMPLATE = ROOT / 'assets' / 'plantilla_housekeeping.xlsx'
SECTIONS = list(QUESTIONS)
FINDING_ROWS = {
 'ORGANIZAR': list(range(5,8)), 'ORDENAR': list(range(8,24)),
 'LIMPIAR': list(range(24,33)), 'ESTANDARIZAR': list(range(33,45)),
 'AUTODISCIPLINA': list(range(45,51))}


def label(text, height=dp(36), bold=False):
    x=Label(text=text, size_hint_y=None, height=height, bold=bold, color=(0.10,0.16,0.19,1), halign='left', valign='middle')
    x.bind(size=lambda i,v: setattr(i,'text_size',(i.width-dp(6),None)))
    return x


class HouseKeepingApp(App):
    title='HouseKeeping - Inspecciones'
    def build(self):
        Window.softinput_mode='below_target'
        self.general={}
        self.answers={}
        self.findings={}
        self.photos={}
        self.body=BoxLayout(orientation='vertical',padding=dp(10),spacing=dp(8))
        head=Label(text='HOUSEKEEPING  |  Inspección',height=dp(42),size_hint_y=None,bold=True,font_size='18sp',color=(0.05,0.3,0.38,1))
        self.body.add_widget(head)
        nav=GridLayout(cols=4,size_hint_y=None,height=dp(49),spacing=dp(3))
        for text,fn in [('Datos',self.page_general),('Checklist',self.page_check),('Hallazgos',self.page_findings),('Fotos',self.page_photos)]:
            b=Button(text=text,font_size='12sp');b.bind(on_release=lambda _x, f=fn:f());nav.add_widget(b)
        self.body.add_widget(nav)
        self.page_holder=BoxLayout(orientation='vertical')
        self.body.add_widget(self.page_holder)
        bottom=Button(text='GENERAR EXCEL (FORMATO ORIGINAL)',height=dp(55),size_hint_y=None,background_color=(0.1,0.52,0.35,1))
        bottom.bind(on_release=lambda *_:self.save_excel())
        self.body.add_widget(bottom)
        self.page_general()
        return self.body

    def page(self):
        self.page_holder.clear_widgets()
        sv=ScrollView(do_scroll_x=False)
        content=BoxLayout(orientation='vertical',size_hint_y=None,padding=(dp(2),dp(6)),spacing=dp(8))
        content.bind(minimum_height=content.setter('height'))
        sv.add_widget(content)
        self.page_holder.add_widget(sv)
        return content

    def page_general(self):
        content=self.page();content.add_widget(label('1. DATOS GENERALES',dp(36),True))
        fields=[('realizado','Realizado por'),('representante','Representante del área'),('supervisor','Supervisor'),('superintendencia','Superintendencia'),('empresa','Empresa'),('lugar','Lugar'),('fecha','Fecha (DD-MM-AAAA)')]
        for key,caption in fields:
            content.add_widget(label(caption,dp(25)))
            if key not in self.general:self.general[key]=TextInput(multiline=False,text=date.today().strftime('%d-%m-%Y') if key=='fecha' else '',size_hint_y=None,height=dp(43))
            inp=self.general[key]
            if inp.parent:inp.parent.remove_widget(inp)
            content.add_widget(inp)

    def page_check(self):
        content=self.page();content.add_widget(label('2. LISTA DE VERIFICACIÓN',dp(36),True))
        for section,items in QUESTIONS.items():
            content.add_widget(label(section,dp(35),True))
            for row,question in items:
                content.add_widget(label(f'{row}. {question}',dp(85)))
                if row not in self.answers:self.answers[row]=Spinner(text='Sin responder',values=('Sin responder','SI','NO','NC'),size_hint_y=None,height=dp(43))
                inp=self.answers[row]
                if inp.parent:inp.parent.remove_widget(inp)
                content.add_widget(inp)

    def page_findings(self):
        content=self.page();content.add_widget(label('3. PLANILLA DE HALLAZGOS',dp(40),True))
        content.add_widget(label('Registra hasta tres hallazgos por categoría',dp(35)))
        for section in SECTIONS:
            content.add_widget(label(section,dp(35),True))
            for index in range(3):
                content.add_widget(label(f'Hallazgo {index+1}',dp(27),True))
                for field,title in [('desv','Desviación'),('resp','Responsable'),('fecha','Fecha cumplimiento'),('obs','Observaciones')]:
                    key=(section,index,field)
                    content.add_widget(label(title,dp(23)))
                    if key not in self.findings:self.findings[key]=TextInput(multiline=field in ('desv','obs'),size_hint_y=None,height=dp(63) if field in ('desv','obs') else dp(43))
                    inp=self.findings[key]
                    if inp.parent:inp.parent.remove_widget(inp)
                    content.add_widget(inp)

    def page_photos(self):
        content=self.page();content.add_widget(label('4. RESPALDO FOTOGRÁFICO',dp(40),True))
        content.add_widget(label('Selecciona fotos de galería o cámara según las aplicaciones disponibles.',dp(48)))
        for i in range(1,10):
            content.add_widget(label(f'REGISTRO {i}',dp(35),True))
            for side in ('antes','despues'):
                btn=Button(text=f'{side.upper()}: {"Foto cargada" if (i,side) in self.photos else "Seleccionar foto"}',size_hint_y=None,height=dp(47))
                btn.bind(on_release=lambda b,idx=i,s=side:self.pick_photo(idx,s,b))
                content.add_widget(btn)

    def pick_photo(self, index, side, button):
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=lambda selected:self.photo_selected(selected,index,side,button),filters=['*.jpg','*.jpeg','*.png','*.webp'])
        except Exception as exc:
            self.notice('Selector de fotos',str(exc))

    def photo_selected(self, selected, index, side, button):
        if not selected:return
        try:
            uri=str(selected[0]);blob=self.read_photo(uri)
            with PILImage.open(io.BytesIO(blob)) as im:
                im.verify()
            self.photos[(index,side)]=blob
            button.text=f'{side.upper()}: Foto cargada ✓'
        except Exception as exc:
            self.notice('No se pudo cargar la foto',str(exc))

    def read_photo(self, uri):
        if uri.startswith('file://'):uri=uri[7:]
        if not uri.startswith('content://'):
            return Path(uri).read_bytes()
        from jnius import autoclass
        PyActivity=autoclass('org.kivy.android.PythonActivity')
        Uri=autoclass('android.net.Uri')
        stream=PyActivity.mActivity.getContentResolver().openInputStream(Uri.parse(uri))
        if not stream:raise RuntimeError('No se pudo abrir la imagen seleccionada')
        out=io.BytesIO()
        try:
            while True:
                part=stream.read()
                if part == -1:break
                out.write(bytes((part & 255,)))
        finally:stream.close()
        return out.getvalue()

    def notice(self,header,message):
        panel=BoxLayout(orientation='vertical',padding=dp(12),spacing=dp(7))
        panel.add_widget(Label(text=str(message),halign='center',valign='middle'))
        b=Button(text='Cerrar',size_hint_y=None,height=dp(45));panel.add_widget(b)
        pop=Popup(title=header,content=panel,size_hint=(.92,.44));b.bind(on_release=pop.dismiss);pop.open()

    def save_excel(self):
        try:
            wb=load_workbook(str(TEMPLATE))
            s=wb['HouseKeeping']
            for cell,k in [('C3','realizado'),('C4','representante'),('C5','supervisor'),('F3','superintendencia'),('F4','empresa'),('C6','lugar'),('F5','fecha')]:
                s[cell]=self.general.get(k).text if k in self.general else ''
            counts={'SI':0,'NO':0,'NC':0}
            for section,items in QUESTIONS.items():
                for row,_ in items:
                    for col in 'FGH':s[f'{col}{row}']=None
                    ans=self.answers[row].text if row in self.answers else ''
                    if ans in counts:
                        counts[ans]+=1
                        s[f'{dict(SI="F",NO="G",NC="H")[ans]}{row}']=ans
            for k,c in [('SI','F'),('NO','G'),('NC','H')]:s[f'{c}65']=counts[k]
            s['F66']='=IF(F65+G65=0,0,F65/(F65+G65))'
            s['F66'].number_format='0%'
            h=wb['Planilla de Hallazgos']
            for section,rows in FINDING_ROWS.items():
                for r in rows:
                    for c in 'BFGH':h[f'{c}{r}']=None
                entries=[]
                for i in range(3):
                    vals=[self.findings.get((section,i,k)).text if (section,i,k) in self.findings else '' for k in ('desv','resp','fecha','obs')]
                    if any(v.strip() for v in vals):entries.append(vals)
                for r,vals in zip(rows,entries):
                    for c,v in zip('BFGH',vals):h[f'{c}{r}']=v
            p=wb['Respaldo Fotograficos']
            # Se conservan logotipos y objetos gráficos de la fila del encabezado.
            p._images=[img for img in p._images if getattr(getattr(img.anchor,'_from',None),'row',-1)==0]
            buffers=[]
            for i in range(1,10):
                for side,col in [('antes','A'),('despues','E')]:
                    raw=self.photos.get((i,side))
                    if not raw:continue
                    im=ImageOps.exif_transpose(PILImage.open(io.BytesIO(raw))).convert('RGB')
                    im.thumbnail((1700,1700))
                    buffer=io.BytesIO();im.save(buffer,format='JPEG',quality=78)
                    buffer.seek(0);buffers.append(buffer)
                    xl=ExcelImage(buffer);xl.width=278;xl.height=145
                    p.add_image(xl,f'{col}{4+(i-1)*8}')
            path=os.path.join(self.user_data_dir,'Inspeccion_HouseKeeping.xlsx')
            wb.save(path)
            message=f'Archivo guardado en los datos de la aplicación:\n{path}'
            # Copia al área compartida Documentos Android cuando está disponible.
            try:
                from androidstorage4kivy import SharedStorage
                shared=SharedStorage()
                result=shared.copy_to_shared(path,'Documents')
                message=f'Excel exportado a Documentos.\n{result}'
            except Exception as err:
                message+='\nNo se pudo copiar a Documentos automáticamente: '+str(err)
            self.notice('Excel generado',message)
        except Exception as exc:
            self.notice('Error al exportar',str(exc))

if __name__ == '__main__':
    HouseKeepingApp().run()
