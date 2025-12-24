"""Entry point for the Animatch app (placeholder)."""
from .api import AnimatchAPI


def main() -> None:
    """Run a simple app demo."""
    api = AnimatchAPI()
    print("Animatch app initialized")
    # placeholder run
    print("Available services:", api.list_services())


if __name__ == "__main__":
    main()
