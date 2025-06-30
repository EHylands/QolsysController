import logging
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta

LOGGER = logging.getLogger(__name__)

class QolsysPKI():
    def __init__(self,keys_directory:str):
        self._id = ''
        self._file_prefix = ''
        self._keys_directory = keys_directory

    def set_id(self,id:str):
        self._id = id
        self._file_prefix = id.replace(':','')

    def check_key_file(self)->bool:
        if os.path.exists(self._keys_directory + self._file_prefix + '.key'):
            LOGGER.debug(f'Found KEY')
            return True
        else:
            LOGGER.debug(f'No KEY File')
            return False
        
    def check_cer_file(self)->bool:
        if os.path.exists(self._keys_directory + self._file_prefix + '.cer'):
            LOGGER.debug('Found CER')
            return True
        else:
            LOGGER.debug(f'No CER File')
            return False
    
    def check_csr_file(self)->bool:
        if os.path.exists(self._keys_directory + self._file_prefix + '.csr'):
            LOGGER.debug(f'Found CSR')
            return True
        else:
            LOGGER.debug(f'No CSR File')
            return False
        
    def check_secure_file(self)->bool:
        if os.path.exists(self._keys_directory + self._file_prefix + '.secure'):
            LOGGER.debug(f'Found Signed Client Certificate')
            return True
        else:
            LOGGER.debug(f'No Signed Client Certificate File')
            return False
        
    def check_qolsys_cer_file(self)->bool:
        if os.path.exists(self._keys_directory  + self._file_prefix + '.qolsys'):
            LOGGER.debug(f'Found Qolsys Certificate')
            return True
        else:
            LOGGER.debug(f'No Qolsys Certificate File')
            return False

    @property
    def key_file_path(self):
        return self._keys_directory + self._file_prefix + '.key'
    
    @property
    def csr_file_path(self):
        return self._keys_directory + self._file_prefix + '.csr'
    
    @property
    def cer_file_path(self):
        return self._keys_directory + self._file_prefix + '.cer'
    
    @property
    def secure_file_path(self):
        return self._keys_directory + self._file_prefix + '.secure'
    
    @property
    def qolsys_cer_file_path(self):
        return self._keys_directory + self._file_prefix + '.qolsys'

    def create(self,mac:str,key_size:int)->bool:

        self.set_id(mac)

        # Check for private key colision
        if os.path.exists(self._keys_directory + self._file_prefix + '.key'):
            LOGGER.error(f'Create KEY File Colision')
            return False
        
        # Check for CER file colision
        if os.path.exists(self._keys_directory + self._file_prefix + '.cer'):
            LOGGER.error(f'Create CER File Colision')
            return False
        
        # Check for CSR file colision
        if os.path.exists(self._keys_directory + self._file_prefix + '.csr'):
            LOGGER.error(f'Create CSR File Colision')
            return False
        
        # Check for CER file colision
        if os.path.exists(self._keys_directory + self._file_prefix + '.secure'):
            LOGGER.error(f'Create Signed Certificate File Colision')
            return False

        LOGGER.debug(f'Creating PKI (' + mac + ')')

        LOGGER.debug(f'Creating KEY')
        private_key = rsa.generate_private_key(public_exponent=65537, 
                                               key_size=key_size)
        private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                format=serialization.PrivateFormat.PKCS8,
                                                encryption_algorithm=serialization.NoEncryption())
        with open(self._keys_directory + self._file_prefix + '.key', "wb") as f:
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
    
        with open(self._keys_directory + self._file_prefix + '.cer' , "wb") as f:    
            f.write(cert_pem)

        LOGGER.debug(f'Creating CSR')
        csr = x509.CertificateSigningRequestBuilder().subject_name(
            subject
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,
        ).sign(private_key, hashes.SHA256())

        # Save CSR to file
        csr_pem = csr.public_bytes(encoding=serialization.Encoding.PEM)
        with open(self._keys_directory + self._file_prefix + '.csr', "wb") as f:
            f.write(csr_pem)
    