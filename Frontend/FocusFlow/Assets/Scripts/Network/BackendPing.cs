using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class BackendPing : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        StartCoroutine(PingBackend());
    }

    IEnumerator PingBackend()
    {
        UnityWebRequest req=UnityWebRequest.Get("http://127.0.0.1:8000/");
        yield return req.SendWebRequest();

        if (req.result == UnityWebRequest.Result.Success)
        {
            Debug.Log("Backend says: "+ req.downloadHandler.text);
        }
        else
        {
            Debug.Log("Backend unreachable");
        }
    }
}
