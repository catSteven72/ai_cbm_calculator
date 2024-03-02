import spacy
from django.conf import settings

nlp = spacy.load(str(settings.TRAINED_MODEL_DIR))


def predict_entities(text):
    doc = nlp(text)

    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

def extract_dims(prediction):
    extracted_info = {}
    current_package = 1
    package_data = {}
    temp_num_pcs = None

    for value, name in prediction:
        if name == "NUM_PCS":
            value = float(value.replace(',', '.'))

            # If dimensions are already started, assign directly to current package
            if any(k in package_data for k in ["LENGTH", "WIDTH", "HEIGHT"]):
                package_data[name] = value
            else:
                temp_num_pcs = value
            continue

        if name in ["LENGTH", "WIDTH", "HEIGHT"]:
            value = float(value.replace(',', '.'))
            package_data[name] = value

        if name == "DIM_UNITS":
            package_data[name] = value

        # Check if a set of dimensions has been completed
        keys_to_check = ["LENGTH", "WIDTH", "HEIGHT"]
        if all(key in package_data for key in keys_to_check):
            # If NUM_PCS was previously stored, assign it to the current package
            if temp_num_pcs is not None:
                package_data["NUM_PCS"] = temp_num_pcs
                temp_num_pcs = None

            extracted_info[current_package] = package_data
            current_package += 1
            package_data = {}

    if package_data:
        if temp_num_pcs is not None and "NUM_PCS" not in package_data:
            package_data["NUM_PCS"] = temp_num_pcs
        extracted_info[current_package] = package_data

    return extracted_info

class Prediction_results():
    def __init__(self, **kwargs):
        self.cbm = None
        self.assumed_dim_units = None
        self.length_meters = None
        self.width_meters = None
        self.height_meters = None
        self.LENGTH = 0
        self.WIDTH = 0
        self.HEIGHT = 0
        self.NUM_PCS = 1

        for key, value in kwargs.items():
            setattr(self, key, value)

    def guess_units(self):
        threshold = 7
        if self.LENGTH < threshold and self.WIDTH < threshold and self.HEIGHT < threshold:
            self.assumed_dim_units = "m"
        else:
            self.assumed_dim_units = "cm"

    def get_dim_units(self):
        if hasattr(self, "DIM_UNITS"):
            if self.DIM_UNITS is not None:
                cms = ["ccm", "cmm", "cms", "cm", "см"]
                inches = ["дюйм", "дюймы", "дюймов", "in", "inches", "inc", "inch", "\""]
                meters = ["meters", "m", "met", "ms", "м", "метр", "метров", "метры"]
                millimeters = ["mm", "мм", "миллиметры", "миллиметров", "милиметров", "миллиметры"]
                if self.DIM_UNITS.lower() in cms:
                    self.assumed_dim_units = "cm"
                    return
                if self.DIM_UNITS.lower() in inches:
                    self.assumed_dim_units = "in"
                    return
                if self.DIM_UNITS.lower() in meters:
                    self.assumed_dim_units = "m"
                    return
                if self.DIM_UNITS.lower() in millimeters:
                    self.assumed_dim_units = "mm"
                    return

        else:
            self.guess_units()
            return self.assumed_dim_units

    def has_all_dims(self):
        if hasattr(self, "LENGTH") and hasattr(self, "WIDTH") and hasattr(self, "HEIGHT"):
            return True
        else:
            return False



    def convert_dims_to_meters(self):

        self.get_dim_units()
        if self.assumed_dim_units == "cm":
            self.length_meters = self.LENGTH/100
            self.width_meters = self.WIDTH/100
            self.height_meters = self.HEIGHT/100
        elif self.assumed_dim_units == "m":
            self.length_meters = self.LENGTH
            self.width_meters = self.WIDTH
            self.height_meters = self.HEIGHT
        elif self.assumed_dim_units == "mm":
            self.length_meters = self.LENGTH/1000
            self.width_meters = self.WIDTH/1000
            self.height_meters = self.HEIGHT/1000
        elif self.assumed_dim_units == "in":
            self.length_meters = self.LENGTH*0.0254
            self.width_meters = self.WIDTH*0.0254
            self.height_meters = self.HEIGHT*0.0254

    def calculate_cbm(self):
        self.cbm = round((self.length_meters*self.width_meters*self.height_meters*self.NUM_PCS), 3)
        return

    def to_dict(self):
        return self.__dict__