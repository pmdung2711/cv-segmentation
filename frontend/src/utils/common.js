import axios from "axios"

export const getBaseURL = () => {
    return axios.create({
        baseURL: "http"
    })
}