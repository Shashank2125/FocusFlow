using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using System.Collections;

public class MissionFetcher : MonoBehaviour
{

   public TextMeshProUGUI missionText;
    void Start() {
        StartCoroutine(GetTodayMission());
    
   }
   IEnumerator GetTodayMission()
    {
        UnityWebRequest req = new UnityWebRequest(
    "http://127.0.0.1:8000/missions/today/2",
    UnityWebRequest.kHttpVerbPOST
);

req.downloadHandler = new DownloadHandlerBuffer();
        yield return req.SendWebRequest();

        if (req.result == UnityWebRequest.Result.Success)
        {
            Mission mission=JsonUtility.FromJson<Mission>(req.downloadHandler.text);
            missionText.text=mission.title+(mission.completed?" (Completed)" : " (Pending)");

        }
        else
        {
            missionText.text="Failed to load mission";
        }
        
    }
}
