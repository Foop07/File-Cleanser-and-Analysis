
import cv2

def detect_logo(document_image_path: str, logo_image_path: str) -> bool:
    """
    Detect if the logo exists in the document image using template matching.

    Args:
        document_image_path (str): Path to the main document image.
        logo_image_path (str): Path to the logo image.

    Returns:
        bool: True if logo is found, False otherwise.
    """
    try:
        doc_img = cv2.imread(document_image_path, cv2.IMREAD_COLOR)
        logo_img = cv2.imread(logo_image_path, cv2.IMREAD_COLOR)

        if doc_img is None or logo_img is None:
            print("[ERROR] Could not load images. Check the paths.")
            return False

        res = cv2.matchTemplate(doc_img, logo_img, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = (res >= threshold).any()
        return loc

    except Exception as e:
        print(f"[ERROR] Logo detection failed: {e}")
        return False
