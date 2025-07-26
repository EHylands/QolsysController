import logging
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509 import load_pem_x509_csr

from cryptography import x509
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta

LOGGER = logging.getLogger(__name__)

class QolsysPKI():
    def __init__(self,keys_directory:str):
        self._id = ''
        self._file_prefix = ''
        self._keys_directory = keys_directory
        self._subkeys_directory = ''

        self._key = None
        self._cer = None
        self._csr = None
        self._secure = None
        self._qolsys = None

    def set_id(self,id:str):
        self._id = id
        self._file_prefix = id.replace(':','').upper()
        self._subkeys_directory = self._keys_directory + self._file_prefix + '/'

    @property
    def key(self):
        return self._key
    
    @property
    def cer(self):
        return self._cer
    
    @property 
    def csr(self):
        return self._csr
    
    @property
    def secure(self):
        return self._secure
    
    @property
    def qolsys(self):
        return self._qolsys

    def load_private_key(self,key:str) -> bool:
        try:
            self._key = serialization.load_pem_private_key(key.encode(),password=None)
            return True
        except ValueError:
            LOGGER.debug(f'Private Key Value Error')
            return False
   
    def load_certificate(self,cer:str) -> bool:
        try:
            self._cer = x509.load_pem_x509_certificate(cer.encode(),None)
            return True
        except ValueError:
            LOGGER.debug(f'Certificate Value Error')
            return False

    def load_certificate_signing_request(self,csr:str) -> bool:
        try:
            self._csr = load_pem_x509_csr(csr.encode())
            return True
        except ValueError:
            LOGGER.debug(f'Certificate Signing Request Value Error')
            return False
        
    def load_qolsys_certificate(self,qolsys:str) -> bool:
        try:
            self._qolsys = x509.load_pem_x509_certificate(qolsys.encode(),None)
            return True
        except ValueError:
            LOGGER.debug(f'Qolsys Certificate Value Error')
            return False
    
    def load_signed_client_certificate(self,secure:str):
        try:
            self._secure = x509.load_pem_x509_certificate(secure.encode(),None)
            return True
        except ValueError:
            LOGGER.debug(f'Client Signed Certificate Value Error')
            return False

    def check_key_file(self)->bool:
        LOGGER.debug(self._subkeys_directory + self._file_prefix + ".key")
        if os.path.exists(self._subkeys_directory + self._file_prefix + '.key'):
            LOGGER.debug(f'Found KEY')
            return True
        else:
            LOGGER.debug(f'No KEY File')
            return False
        
    def check_cer_file(self)->bool:
        if os.path.exists(self._subkeys_directory + self._file_prefix + '.cer'):
            print(self._subkeys_directory  + self._file_prefix + '.cer')

            LOGGER.debug('Found CER')
            return True
        else:
            LOGGER.debug(f'No CER File')
            return False
    
    def check_csr_file(self)->bool:
        if os.path.exists(self._subkeys_directory + self._file_prefix + '.csr'):
            LOGGER.debug(f'Found CSR')
            return True
        else:
            LOGGER.debug(f'No CSR File')
            return False
        
    def check_secure_file(self)->bool:
        if os.path.exists(self._subkeys_directory + self._file_prefix + '.secure'):
            LOGGER.debug(f'Found Signed Client Certificate')
            return True
        else:
            LOGGER.debug(f'No Signed Client Certificate File')
            return False
        
    def check_qolsys_cer_file(self)->bool:
        LOGGER.debug(self._subkeys_directory + self._file_prefix + ".qolsys")
        if os.path.exists(self._subkeys_directory  + self._file_prefix + '.qolsys'):
            LOGGER.debug(f'Found Qolsys Certificate')
            return True
        else:
            LOGGER.debug(f'No Qolsys Certificate File')
            return False

    @property
    def key_file_path(self):
        return self._subkeys_directory + self._file_prefix + '.key'
    
    @property
    def csr_file_path(self):
        return self._subkeys_directory + self._file_prefix + '.csr'
    
    @property
    def cer_file_path(self):
        return self._subkeys_directory + self._file_prefix + '.cer'
    
    @property
    def secure_file_path(self):
        return self._subkeys_directory + self._file_prefix + '.secure'
    
    @property
    def qolsys_cer_file_path(self):
        return self._subkeys_directory + self._file_prefix + '.qolsys'

    def create(self,mac:str,key_size:int)->bool:

        self.set_id(mac)

        # Check if directory exist 
        if os.path.exists(self._subkeys_directory + self._file_prefix + '.key'):
            LOGGER.error(f'Create Directory Colision')
            return False

        # Check for private key colision
        if os.path.exists(self._subkeys_directory + self._file_prefix + '.key'):
            LOGGER.error(f'Create KEY File Colision')
            return False
        
        # Check for CER file colision
        if os.path.exists(self._subkeys_directory + self._file_prefix + '.cer'):
            LOGGER.error(f'Create CER File Colision')
            return False
        
        # Check for CSR file colision
        if os.path.exists(self._subkeys_directory + self._file_prefix + '.csr'):
            LOGGER.error(f'Create CSR File Colision')
            return False
        
        # Check for CER file colision
        if os.path.exists(self._subkeys_directory + self._file_prefix + '.secure'):
            LOGGER.error(f'Create Signed Certificate File Colision')
            return False

        LOGGER.debug(f'Creating PKI (' + mac + ')')

        LOGGER.debug(f'Creating PKI Directory')
        os.makedirs(self._subkeys_directory)

        LOGGER.debug(f'Creating KEY')
        private_key = rsa.generate_private_key(public_exponent=65537, 
                                               key_size=key_size)
        private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                format=serialization.PrivateFormat.PKCS8,
                                                encryption_algorithm=serialization.NoEncryption())
        with open(self._subkeys_directory + self._file_prefix + '.key', "wb") as f:
            f.write(private_pem)
        
        LOGGER.debug(f'Creating CER')
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "SanJose"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, ""),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Qolsys Inc."),
            x509.NameAttribute(NameOID.COMMON_NAME, "www.qolsys.com ")
]       )
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,
        ).sign(private_key, hashes.SHA256())
        cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)
    
        with open(self._subkeys_directory + self._file_prefix + '.cer' , "wb") as f:    
            f.write(cert_pem)

        LOGGER.debug(f'Creating CSR')
        csr = x509.CertificateSigningRequestBuilder().subject_name(
            subject
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,
        ).sign(private_key, hashes.SHA256())

        # Save CSR to file
        csr_pem = csr.public_bytes(encoding=serialization.Encoding.PEM)
        with open(self._subkeys_directory + self._file_prefix + '.csr', "wb") as f:
            f.write(csr_pem)
    