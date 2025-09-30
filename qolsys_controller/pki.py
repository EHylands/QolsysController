import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509 import load_pem_x509_csr
from cryptography.x509.oid import NameOID

from .settings import QolsysSettings

LOGGER = logging.getLogger(__name__)


class QolsysPKI:
    def __init__(self, settings: QolsysSettings) -> None:
        self._id = ""
        self._subkeys_directory: Path = Path

        self._key = None
        self._cer = None
        self._csr = None
        self._secure = None
        self._qolsys = None

        self._settings = settings

    @property
    def id(self) -> str:
        return self._id

    def formatted_id(self) -> str:
        return ":".join(self.id[i:i+2] for i in range(0, len(self.id), 2))

    def set_id(self, pki_id: str) -> None:
        self._id = pki_id.replace(":", "").lower()
        LOGGER.debug("Using PKI: %s", self.formatted_id())
        self._subkeys_directory = self._settings.pki_directory.joinpath(Path(self.id))

    @property
    def key(self) -> str:
        return self._key

    @property
    def cer(self) -> str:
        return self._cer

    @property
    def csr(self) -> str:
        return self._csr

    @property
    def secure(self) -> str:
        return self._secure

    @property
    def qolsys(self) -> str:
        return self._qolsys

    def auto_discover_pki(self) -> bool:
        pattern = r"^[A-Fa-f0-9]{12}$"

        LOGGER.debug("Auto Discovery Enabled")
        with os.scandir(self._settings.pki_directory) as entries:
            for entry in entries:
                if entry.is_dir() and re.fullmatch(pattern, entry.name):
                    self.set_id(entry.name)
                    return True

        return False

    def load_private_key(self, key: str) -> bool:
        try:
            self._key = serialization.load_pem_private_key(key.encode(), password=None)
        except ValueError:
            LOGGER.debug("Private Key Value Error")
            return False

        return True

    def load_certificate(self, cer: str) -> bool:
        try:
            self._cer = x509.load_pem_x509_certificate(cer.encode(), None)
        except ValueError:
            LOGGER.debug("Certificate Value Error")
            return False

        return True

    def load_certificate_signing_request(self, csr: str) -> bool:
        try:
            self._csr = load_pem_x509_csr(csr.encode())
        except ValueError:
            LOGGER.debug("Certificate Signing Request Value Error")
            return False

        return True

    def load_qolsys_certificate(self, qolsys: str) -> bool:
        try:
            self._qolsys = x509.load_pem_x509_certificate(qolsys.encode(), None)
        except ValueError:
            LOGGER.debug("Qolsys Certificate Value Error")
            return False

        return True

    def load_signed_client_certificate(self, secure: str) -> bool:
        try:
            self._secure = x509.load_pem_x509_certificate(secure.encode(), None)
        except ValueError:
            LOGGER.debug("Client Signed Certificate Value Error")
            return False

        return True

    def check_key_file(self) -> bool:
        if self._subkeys_directory.joinpath(self.id + ".key").resolve().exists():
            LOGGER.debug("Found KEY")
            return True
        LOGGER.debug("No KEY File")
        return False

    def check_cer_file(self) -> bool:
        if self._subkeys_directory.joinpath(self.id + ".cer").resolve().exists():
            LOGGER.debug("Found CER")
            return True
        LOGGER.debug("No CER File")
        return False

    def check_csr_file(self) -> bool:
        if self._subkeys_directory.joinpath(self.id + ".csr").resolve().exists():
            LOGGER.debug("Found CSR")
            return True
        LOGGER.debug("No CSR File")
        return False

    def check_secure_file(self) -> bool:
        if self._subkeys_directory.joinpath(self.id + ".secure").resolve().exists():
            LOGGER.debug("Found Signed Client Certificate")
            return True
        LOGGER.debug("No Signed Client Certificate File")
        return False

    def check_qolsys_cer_file(self) -> bool:
        if self._subkeys_directory.joinpath(self.id + ".qolsys").resolve().exists():
            LOGGER.debug("Found Qolsys Certificate")
            return True
        LOGGER.debug("No Qolsys Certificate File")
        return False

    @property
    def key_file_path(self) -> Path:
        return self._subkeys_directory.joinpath(self.id + ".key")

    @property
    def csr_file_path(self) -> str:
        return self._subkeys_directory.joinpath(self.id + ".csr")

    @property
    def cer_file_path(self) -> str:
        return self._subkeys_directory.joinpath(self.id + ".cer")

    @property
    def secure_file_path(self) -> str:
        return self._subkeys_directory.joinpath(self.id + ".secure")

    @property
    def qolsys_cer_file_path(self) -> str:
        return self._subkeys_directory.joinpath(self.id + ".qolsys")

    def create(self, mac: str, key_size: int) -> bool:

        self.set_id(mac)

        # Check if directory exist
        if self._subkeys_directory.resolve().exists():
            LOGGER.error("Create Directory Colision")
            return False

        # Check for private key colision
        if self._subkeys_directory.joinpath(self.id + ".key").resolve().exists():
            LOGGER.error("Create KEY File Colision")
            return False

        # Check for CER file colision
        if self._subkeys_directory.joinpath(self.id + ".cer").resolve().exists():
            LOGGER.error("Create CER File Colision")
            return False

        # Check for CSR file colision
        if self._subkeys_directory.joinpath(self.id + ".csr").resolve().exists():
            LOGGER.error("Create CSR File Colision")
            return False

        # Check for CER file colision
        if self._subkeys_directory.joinpath(self.id + ".secure").resolve().exists():
            LOGGER.error("Create Signed Certificate File Colision")
            return False

        LOGGER.debug("Creating PKI:  %s", self.formatted_id())

        LOGGER.debug("Creating PKI Directory")
        self._subkeys_directory.resolve().mkdir(parents=True)

        LOGGER.debug("Creating KEY")
        private_key = rsa.generate_private_key(public_exponent=65537,
                                               key_size=key_size)
        private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                format=serialization.PrivateFormat.PKCS8,
                                                encryption_algorithm=serialization.NoEncryption())
        with self._subkeys_directory.joinpath(self.id + ".key").open("wb") as file:
            file.write(private_pem)

        LOGGER.debug("Creating CER")
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "SanJose"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, ""),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Qolsys Inc."),
            x509.NameAttribute(NameOID.COMMON_NAME, "www.qolsys.com "),
        ])
        cert = x509.CertificateBuilder().subject_name(
            subject,
        ).issuer_name(
            issuer,
        ).public_key(
            private_key.public_key(),
        ).serial_number(
            x509.random_serial_number(),
        ).not_valid_before(
            datetime.utcnow(),
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365),
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,
        ).sign(private_key, hashes.SHA256())
        cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)

        with self._subkeys_directory.joinpath(self.id + ".cer").open("wb") as file:
            file.write(cert_pem)

        LOGGER.debug("Creating CSR")
        csr = x509.CertificateSigningRequestBuilder().subject_name(
            subject,
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,
        ).sign(private_key, hashes.SHA256())

        # Save CSR to file
        csr_pem = csr.public_bytes(encoding=serialization.Encoding.PEM)
        with self._subkeys_directory.joinpath(self.id + ".csr").open("wb") as file:
            file.write(csr_pem)

        return True
