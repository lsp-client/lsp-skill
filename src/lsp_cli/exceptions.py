from attrs import define


@define
class CapabilityCommandException(Exception):
    client_id: str

    def __str__(self) -> str:
        return f"Capability command failed for client ID: {self.client_id}"
