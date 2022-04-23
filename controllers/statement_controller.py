"""
   IMPORTS
"""
from os import remove
import re
import pdfplumber
from classes.Item import Item
from classes.Card import Card
from classes.Statement import Statement
from classes.ItemsSet import ItemsSet


class StatementController():
    """
    Handles the logic of the statements.
    """
    #Regexs
    DATE_REGEX = [
                   '.*?^([0-9][0-9](/|-)[0-9][0-9](/|-)[0-9][0-9])$.*',
                   '^(([0-9])|([0][0-9])|([1-2][0-9])|([3][0-1]))\-(Ene|Feb|Mar|Apr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dic)\-\d{2}$',
                   '^(([0-9])|([0][0-9])|([1-2][0-9])|([3][0-1]))\-(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiem.|Octubre|Noviem.|Diciem.)\-\d{2}$'
                 ]
    CARD_TOTAL = [
                    'TOTAL CONSUMOS DE',
                    'TOTAL TARJETA',
                    'TOTAL CONSUMOS',
                    'TOTAL TITULAR',
                    'TOTAL ADICIONAL',
                    'Total de cuotas a vencer'
                 ]
    QUOTE_REGEX = '[0-50]/[0-50]'

    #Prefixs
    QUOTE_PREFIX = [
                     'CUOTA',
                     'C.'
                   ]

    #Taxes
    IMPUESTOS = [
                  'IMPUESTO'
                ]
    IVA = [
            'IVA',
            'I.V.A'
          ]
    INTERESES_FINANCIACION = [
                               'INTERESES'
                             ]

    #Invalid Line values
    INVALID_LINES = [
                      'SU PAGO EN PESOS', 
                      'SU PAGO'
                    ]

    #Values
    IVA_VALUE = 0.21

    def __init__(self):
        self.statement = Statement()
        self.list_splitted_item = []

    def statement_orc_scanner_visa(self,pdf_path,bank='ICBC',entity='VISA'):
        
        #Get pdf text
        text = self.extract_text_from_statement_pdf(pdf_path)
        items_set = ItemsSet(items=[])
        taxes_got = False

        for line in text.split('\n'):
            self.list_splitted_item = list(filter(lambda x: len(x) > 0, line.split(' ')))

            #For MASTERCARD only: looking for taxes at the begining
            if entity == 'MASTERCARD' and not taxes_got:
                taxes_items_set = ItemsSet(items=[])

                if self.is_tax() and not self.filter_tax_by_amount():
                    ars_amount = self.extract_ars_amount()
                    concept = self.extract_concept()
                    item = Item(concept=concept,ars_amount=ars_amount,type='taxes')
                    taxes_items_set.append_item(item)

                if len(taxes_items_set.items) > 0:
                    taxes_items_set.type = 'taxes'
                    self.statement.append_items_set(taxes_items_set)

            if any(x in line.upper() for x in getattr(self,'CARD_TOTAL')):
                #Set Card Value for ItemSet
                items_set.card = Card(entity=entity,bank=bank,last_four_numbers=self.extract_last_four_numbers()) if entity == 'VISA' else Card(entity=entity,bank=bank) if entity == 'MASTERCARD' else None
                self.statement.append_items_set(items_set)
                items_set = ItemsSet(items=[])
            
            date = self.multi_regex_match('DATE_REGEX')
            if (date!= False and 
                self.is_valid_line(line) and 
                not self.is_multi_date_line()):
                
                taxes_got = True
                quote = self.extract_quote()
                receipt = self.exctract_receipt(entity=entity)
                ars_amount = self.extract_ars_amount()
                concept = self.extract_concept()

                if not self.is_tax(concept):
                    item = Item(date=date,concept=concept,ars_amount=ars_amount,receipt=receipt,type='buy')
                    item.set_quotes_values_from_string(quote)
                else:
                    ars_amount = ars_amount if concept not in getattr(self,'IVA') and entity == 'VISA' else round(ars_amount * getattr(self,'IVA_VALUE'),2)
                    item = Item(date=date,concept=concept,ars_amount=ars_amount,type='taxes')
                
                items_set.append_item(item)
                    
        #Append Taxes Items Set
        if entity == 'VISA':
            items_set.type = 'taxes'
            self.statement.append_items_set(items_set)
    
    def extract_date(self):
        try:
            dates = [list(filter(re.compile(regex).match, self.list_splitted_item))[0] for regex in getattr(self,'DATE_REGEX') if list(filter(re.compile(regex).match, self.list_splitted_item)) != []]
            self.list_splitted_item.remove(dates[0])    
            return dates[0]
        except:
            return None
        
    def filter_tax_by_amount(self):
        for word in self.list_splitted_item:
            try:
                if ',' in word or '.' in word:
                    float(word.replace(' ','').replace('.','').replace(',','.'))
                    return False
            except:
                continue
        return True

    def extract_last_four_numbers(self):
        return int([x for x in self.list_splitted_item if self.is_number(x)][0])

    def extract_quote(self):
        r = re.compile(getattr(self,'QUOTE_REGEX'))
        quote = list(filter(r.search, self.list_splitted_item))
        
        quote_prefixs = [x for word in getattr(self,'QUOTE_PREFIX') for x in self.list_splitted_item if word in x.upper() and not re.search(getattr(self,'QUOTE_REGEX'),x)]
        [self.list_splitted_item.remove(x) for x in quote_prefixs]

        if len(quote) > 0:
            self.list_splitted_item.remove(quote[0])
            prefixes = [prefix for prefix in getattr(self,'QUOTE_PREFIX') if prefix in quote[0]]
            for prefix in prefixes: quote[0] = quote[0].upper().replace(prefix,'')
            return quote[0]
        else:
            return '01/01'

    def exctract_receipt(self,entity):
        receipts = [x for x in self.list_splitted_item if x.endswith('*')]
        if len(receipts) < 1 or not receipts[0].replace('*','').isdigit():
            receipts = [x for x in self.list_splitted_item if x.isdigit()]      
        
        if '*' in self.list_splitted_item: self.list_splitted_item.remove('*')
        
        if len(receipts) > 0:
            self.list_splitted_item.remove(receipts[0]) if receipts[0] in self.list_splitted_item else None
            return receipts[0].replace('*','')
    
    def extract_ars_amount(self):
        for element in self.list_splitted_item[::-1]:
            number = element.strip(' ').replace('.','').replace(',','.')
            if self.is_number(number):
                self.list_splitted_item.remove(element)
                return round(float(number),2)

    def extract_concept(self):
        return " ".join(self.list_splitted_item) + " "

    def is_tax(self,concept=None):
        if concept is None: concept = self.list_splitted_item[0] if len(self.list_splitted_item) > 1 else False
        if not concept: return False
        
        taxes = getattr(self,'IMPUESTOS') + getattr(self,'IVA') + getattr(self,'INTERESES_FINANCIACION')
        for tax in taxes:
            if any(tax in word.upper() for word in list(filter(lambda x: len(x) > 0, concept.upper().split(' ')))): return True
        return False


    def is_valid_line(self,line):
        return not any(invalid_line in line for invalid_line in getattr(self,'INVALID_LINES'))

    def is_multi_date_line(self):
        return True if len([el for regex in getattr(self,'DATE_REGEX') for el in self.list_splitted_item if re.match(regex,el)]) > 1 else False

    def multi_regex_match(self,attr):
        value = self.list_splitted_item[0] if len(self.list_splitted_item) > 1 else ''
        if not any(re.match(regex,value) for regex in getattr(self,attr)):
            value = '-'.join(self.list_splitted_item[0:3]) if len(self.list_splitted_item) > 2 else ''
            for ele in self.list_splitted_item[0:3]: self.list_splitted_item.remove(ele)
            return value if any(re.match(regex,value) for regex in getattr(self,attr)) else False
        else:
            return self.extract_date()

    @staticmethod
    def is_number(value):
        value = value.strip(' ').replace(',','.')
        return True if type(value) in [int, float] else str(value).replace('.','',1).isdigit()

    @staticmethod
    def extract_text_from_statement_pdf(pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            return ''.join([page.extract_text() for page in pdf.pages])