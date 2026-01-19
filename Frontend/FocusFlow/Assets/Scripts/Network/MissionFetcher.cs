using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using System.Collections;
using UnityEngine.UI;

public class MissionFetcher : MonoBehaviour
{
    public Mission currentMission;
    public Button completeButton;



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
            currentMission=mission;
            UpdateUI();


        }
        else
        {
            missionText.text="Failed to load mission";
        }
        
    }
    public void UpdateUI()
    {
        missionText.text=
        currentMission.title+(currentMission.completed?" (Completed)": " (Pending)");
        completeButton.interactable=!currentMission.completed;

    }
    public void CompleteMission()
    {
        if (currentMission==null||currentMission.completed)
        return;
        StartCoroutine(CompleteMissionRequest());
    }
    IEnumerator CompleteMissionRequest()
    {
        string url="http://127.0.0.1:8000/missions/complete/"+currentMission.id;
        UnityWebRequest req=new UnityWebRequest(url,"POST");
        req.downloadHandler=new DownloadHandlerBuffer();
        yield return req.SendWebRequest();
        if (req.result == UnityWebRequest.Result.Success)
        {
            currentMission.completed=true;
            UpdateUI();
        }
        else
        {
            Debug.LogError(req.error);
        }
    }
}
