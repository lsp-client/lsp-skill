from attrs import define


@define
class CapabilityCommandException(Exception):
    client_id: str
    message: str | None = None

    def __str__(self) -> str:
        if self.message:
            return f"{self.message} (client ID: {self.client_id})"
        return f"Capability command failed for client ID: {self.client_id}"
