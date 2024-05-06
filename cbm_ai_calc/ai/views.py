from . import ai_model
from . import preprocessor

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import bleach

class ProcessFormAPI(APIView):

    def post(self, request):
        input_text = request.data.get("inputText", "")

        cleaned_input = bleach.clean(input_text)
        if not cleaned_input:
            response_data = {
                "output_text": "",
                "total_cbm": "",
                "original_input": ""
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        preprocessed_user_input = preprocessor.preprocess_user_input(cleaned_input)

        predicted_entities = ai_model.predict_entities(preprocessed_user_input)

        extracted_dims = ai_model.extract_dims(predicted_entities)

        predicted_object_list = []

        for dim in extracted_dims:
            instance = ai_model.Prediction_results(**extracted_dims[dim])

            predicted_object_list.append(instance)
            instance.convert_dims_to_meters()
            instance.calculate_cbm()


        total_cbm = sum(obj.cbm for obj in predicted_object_list)

        output_text = [obj.to_dict() for obj in predicted_object_list]

        response_data = {
            "output_text": output_text,
            "total_cbm": round(total_cbm, 3),
            "original_input": input_text
        }

        return Response(response_data, status=status.HTTP_200_OK)